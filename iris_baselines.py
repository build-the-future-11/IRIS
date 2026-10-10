from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
import tempfile
from dataclasses import asdict, dataclass
from numbers import Real
from pathlib import Path
from typing import Any

import numpy as np

PROTECTED_IDS = set(range(1000, 1030))
DEVELOPMENT_RECORD_SCHEMA = "iris.scalar_baselines.development.v2"
_IMPORTED_SOURCE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _checked_source_identity() -> str:
    """Refuse to label imported functions with subsequently replaced file bytes."""
    message = "development source identity changed or is unavailable; use a fresh interpreter"
    try:
        current = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except OSError as exc:
        raise ValueError(message) from exc
    if current != _IMPORTED_SOURCE_SHA256:
        raise ValueError(message)
    return _IMPORTED_SOURCE_SHA256


def _finite_real(value: Any, name: str, *, positive: bool = False) -> None:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number")
    if not math.isfinite(value) or (positive and value <= 0):
        suffix = "positive and finite" if positive else "finite"
        raise ValueError(f"{name} must be {suffix}")


def _observations(values: np.ndarray, name: str = "observations") -> np.ndarray:
    array = np.asarray(values)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"{name} must be a non-empty 1D array")
    if array.dtype.kind not in "iuf" or not np.isfinite(array).all():
        raise ValueError(f"{name} must contain finite real numbers")
    array = array.astype(float)
    if not np.isfinite(array).all():
        raise ValueError(f"{name} exceeds the float64 range")
    return array


ROBKF_REFERENCE = {
    "repository": "Fisch-Alex/Robkf",
    "commit": "0c4287545034bace38b1e8fb795726add61032b5",
    "ao_wrapper": "R/AORKF_huber.R",
    "ao_update": "src/aorkf_huber_matrix.cpp",
    "io_wrapper": "R/IORKF_huber.R",
    "io_update": "src/iorkf_huber_matrix.cpp",
}


@dataclass(frozen=True)
class LinearGaussianModel:
    transition: float = 1.0
    observation: float = 1.0
    process_var: float = 0.05
    observation_var: float = 0.25
    initial_mean: float = 0.0
    initial_var: float = 1.0

    def validate(self) -> None:
        for name in ("transition", "observation", "initial_mean"):
            _finite_real(getattr(self, name), name)
        for name in ("process_var", "observation_var", "initial_var"):
            _finite_real(getattr(self, name), name, positive=True)


@dataclass(frozen=True)
class RunConfig:
    experiment_id: int
    scenario: str
    length: int = 200
    huber_c: float = 1.5
    ao_h: float = 2.0
    io_h: float = 2.0

    def validate(self) -> None:
        if (
            isinstance(self.experiment_id, bool)
            or not isinstance(self.experiment_id, int)
            or self.experiment_id < 0
        ):
            raise ValueError("experiment_id must be a non-negative integer")
        if self.experiment_id in PROTECTED_IDS:
            raise ValueError(
                f"Protected confirmatory experiment ID {self.experiment_id} is closed"
            )
        if (
            isinstance(self.length, bool)
            or not isinstance(self.length, int)
            or self.length < 4
        ):
            raise ValueError("length must be an integer >= 4")
        for name in ("huber_c", "ao_h", "io_h"):
            _finite_real(getattr(self, name), name, positive=True)
        if self.scenario not in {
            "clean",
            "additive_outlier",
            "persistent_shift",
            "false_open",
            "mixed",
        }:
            raise ValueError(f"Unknown scenario: {self.scenario}")


def _seed(experiment_id: int) -> int:
    return int(hashlib.sha256(f"iris-dev:{experiment_id}".encode()).hexdigest()[:8], 16)


def generate_sequence(
    config: RunConfig, model: LinearGaussianModel
) -> dict[str, np.ndarray]:
    config.validate()
    model.validate()
    rng = np.random.default_rng(_seed(config.experiment_id))
    x = np.zeros(config.length, dtype=float)
    y = np.zeros(config.length, dtype=float)
    shift_start = config.length // 2
    for t in range(1, config.length):
        drift = 0.0
        if config.scenario in {"persistent_shift", "mixed"} and t >= shift_start:
            drift = 0.35
        x[t] = (
            model.transition * x[t - 1]
            + drift
            + rng.normal(0.0, math.sqrt(model.process_var))
        )
    y[:] = model.observation * x + rng.normal(
        0.0, math.sqrt(model.observation_var), size=config.length
    )
    if config.scenario in {"additive_outlier", "mixed"}:
        for idx in (config.length // 4, 3 * config.length // 4):
            y[idx] += 8.0 * math.sqrt(model.observation_var)
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("generated sequence exceeds the finite numeric range")
    return {"state": x, "observation": y}


def _huber_weight(z: float, c: float) -> float:
    az = abs(z)
    return 1.0 if az <= c else c / az


def _clip_scalar(value: float, threshold: float) -> tuple[float, float]:
    """Scalar form of RobKF's Euclidean-norm clipping.

    Returns (clipped_value, multiplicative_weight). The maintained RobKF
    implementation clips the norm of the relevant update vector at h.
    In one dimension, the Euclidean norm is abs(value).
    """
    magnitude = abs(value)
    if magnitude <= threshold or magnitude == 0.0:
        return value, 1.0
    weight = threshold / magnitude
    # The ratio can underflow even when the clipped correction is representable.
    return math.copysign(threshold, value), weight


def _product_ratio(
    left: float, right: float, denominator: float, *, extra_factor: float = 1.0
) -> float:
    """Evaluate left * right * extra_factor / denominator without losing scale.

    Callers supply finite values and a positive denominator. The significands
    stay near unity; powers of two are combined exactly before one final scale.
    A truly unrepresentable result still returns zero or raises explicitly.
    """
    left_mantissa, left_exponent = math.frexp(left)
    right_mantissa, right_exponent = math.frexp(right)
    denominator_mantissa, denominator_exponent = math.frexp(denominator)
    extra_mantissa, extra_exponent = math.frexp(extra_factor)
    try:
        return math.ldexp(
            left_mantissa * right_mantissa * extra_mantissa / denominator_mantissa,
            left_exponent + right_exponent + extra_exponent - denominator_exponent,
        )
    except OverflowError as exc:
        raise ValueError("filter ratio exceeds the finite numeric range") from exc


def _kalman_terms(
    m: float,
    p: float,
    obs: float,
    model: LinearGaussianModel,
) -> tuple[float, float, float, float, float]:
    m_pred = model.transition * m
    p_pred = model.transition * p * model.transition + model.process_var
    innovation = obs - model.observation * m_pred
    s = model.observation * p_pred * model.observation + model.observation_var
    if (
        not all(math.isfinite(value) for value in (m_pred, p_pred, innovation, s))
        or s <= 0
    ):
        raise ValueError("Kalman prediction exceeds the finite numeric range")
    gain = _product_ratio(p_pred, model.observation, s)
    if not math.isfinite(gain):
        raise ValueError("Kalman gain exceeds the finite numeric range")
    return m_pred, p_pred, innovation, gain, s


def _state_correction(
    p_pred: float,
    innovation: float,
    gain: float,
    innovation_var: float,
    model: LinearGaussianModel,
) -> float:
    """Retain K*innovation even when the intermediate gain underflows.

    Preserve ordinary arithmetic when gain and correction are normal floats.
    Otherwise combine P*C*innovation/S before scaling into the float64 range.
    """
    correction = gain * innovation
    if (
        math.isfinite(correction)
        and abs(gain) >= sys.float_info.min
        and abs(correction) >= sys.float_info.min
    ):
        return correction
    return _product_ratio(
        p_pred, model.observation, innovation_var, extra_factor=innovation
    )


def _posterior_variance(
    p_pred: float, innovation_var: float, model: LinearGaussianModel
) -> float:
    # Algebraically (1 - K*C)*P. Scaled multiplication avoids cancellation
    # and premature underflow of R/S when P*R/S is still representable.
    value = _product_ratio(p_pred, model.observation_var, innovation_var)
    if not math.isfinite(value) or value <= 0:
        raise ValueError("posterior variance exceeds the positive finite numeric range")
    return value


def filter_sequence(
    observations: np.ndarray,
    model: LinearGaussianModel,
    *,
    huber_c: float | None = None,
) -> dict[str, np.ndarray]:
    """Classical B0 filter, or the historical IRIS B1 residual-Huber control."""
    model.validate()
    observations = _observations(observations)
    if huber_c is not None:
        _finite_real(huber_c, "huber_c", positive=True)

    means = np.zeros_like(observations)
    variances = np.zeros_like(observations)
    innovations = np.zeros_like(observations)
    standardized = np.zeros_like(observations)
    weights = np.ones_like(observations)

    m = model.initial_mean
    p = model.initial_var
    for t, obs in enumerate(observations):
        m_pred, p_pred, innovation, gain, s = _kalman_terms(m, p, float(obs), model)
        z = innovation / math.sqrt(s)
        weight = 1.0 if huber_c is None else _huber_weight(z, huber_c)
        effective_innovation = innovation
        if huber_c is not None and weight < 1.0:
            effective_innovation = math.copysign(huber_c * math.sqrt(s), innovation)
        m = m_pred + _state_correction(p_pred, effective_innovation, gain, s, model)
        p = _posterior_variance(p_pred, s, model)
        if not math.isfinite(m) or not math.isfinite(z):
            raise ValueError("filter update exceeds the finite numeric range")

        means[t] = m
        variances[t] = p
        innovations[t] = innovation
        standardized[t] = z
        weights[t] = weight

    return {
        "mean": means,
        "variance": variances,
        "innovation": innovations,
        "standardized_innovation": standardized,
        "robust_weight": weights,
    }


def aorkf_huber_sequence(
    observations: np.ndarray,
    model: LinearGaussianModel,
    *,
    h: float = 2.0,
) -> dict[str, np.ndarray]:
    """B2: scalar AO-robust Huber Kalman update matching maintained RobKF.

    RobKF AORKF_huber computes the ordinary Kalman correction K * innovation
    and clips the Euclidean norm of that *state correction* at h before
    applying it. The covariance update remains the ordinary Kalman covariance
    update. This is intentionally distinct from B1, which Huber-weights the
    standardized observation residual before multiplying by K.

    Source pin:
      Fisch-Alex/Robkf@0c4287545034bace38b1e8fb795726add61032b5
      src/aorkf_huber_matrix.cpp
    """
    model.validate()
    observations = _observations(observations)
    _finite_real(h, "h", positive=True)
    means = np.zeros_like(observations)
    variances = np.zeros_like(observations)
    innovations = np.zeros_like(observations)
    corrections = np.zeros_like(observations)
    weights = np.ones_like(observations)

    m = model.initial_mean
    p = model.initial_var
    for t, obs in enumerate(observations):
        m_pred, p_pred, innovation, gain, s = _kalman_terms(m, p, float(obs), model)
        raw_update = _state_correction(p_pred, innovation, gain, s, model)
        if not math.isfinite(raw_update):
            raise ValueError("AO correction exceeds the finite numeric range")
        update, weight = _clip_scalar(raw_update, h)
        m = m_pred + update
        p = _posterior_variance(p_pred, s, model)
        if not math.isfinite(m):
            raise ValueError("AO update exceeds the finite numeric range")

        means[t] = m
        variances[t] = p
        innovations[t] = innovation
        corrections[t] = update
        weights[t] = weight

    return {
        "mean": means,
        "variance": variances,
        "innovation": innovations,
        "robust_component": corrections,
        "robust_weight": weights,
    }


def iorkf_huber_sequence(
    observations: np.ndarray,
    model: LinearGaussianModel,
    *,
    h: float = 2.0,
) -> dict[str, np.ndarray]:
    """B3: scalar IO-robust Huber Kalman update matching maintained RobKF.

    RobKF IORKF_huber clips (I - C K) * innovation and then reconstructs
    the state update as C^{-1} * (innovation - clipped_component). In the
    scalar IRIS harness C is model.observation, so this translation is exact
    for the one-dimensional linear-Gaussian model. The covariance update
    remains the ordinary Kalman covariance update.

    Source pin:
      Fisch-Alex/Robkf@0c4287545034bace38b1e8fb795726add61032b5
      src/iorkf_huber_matrix.cpp
    """
    model.validate()
    observations = _observations(observations)
    _finite_real(h, "h", positive=True)

    if model.observation == 0:
        raise ValueError(
            "observation must be non-zero for the scalar IO-robust baseline"
        )

    means = np.zeros_like(observations)
    variances = np.zeros_like(observations)
    innovations = np.zeros_like(observations)
    robust_components = np.zeros_like(observations)
    weights = np.ones_like(observations)

    m = model.initial_mean
    p = model.initial_var
    for t, obs in enumerate(observations):
        m_pred, p_pred, innovation, gain, s = _kalman_terms(m, p, float(obs), model)
        raw_component = _product_ratio(innovation, model.observation_var, s)
        robust_component, weight = _clip_scalar(raw_component, h)
        # Equivalent to (innovation - clipped_component)/C. Splitting off
        # the Kalman correction preserves the h->infinity limit for tiny C.
        m = (
            m_pred
            + _state_correction(p_pred, innovation, gain, s, model)
            + (raw_component - robust_component) / model.observation
        )
        p = _posterior_variance(p_pred, s, model)
        if not math.isfinite(m) or not math.isfinite(raw_component):
            raise ValueError("IO update exceeds the finite numeric range")

        means[t] = m
        variances[t] = p
        innovations[t] = innovation
        robust_components[t] = robust_component
        weights[t] = weight

    return {
        "mean": means,
        "variance": variances,
        "innovation": innovations,
        "robust_component": robust_components,
        "robust_weight": weights,
    }


def summarize(
    truth: np.ndarray, estimate: np.ndarray, weights: np.ndarray
) -> dict[str, float]:
    truth = _observations(truth, "truth")
    estimate = _observations(estimate, "estimate")
    weights = _observations(weights, "weights")
    if truth.shape != estimate.shape or truth.shape != weights.shape:
        raise ValueError("truth, estimate and weights must have identical shapes")
    if np.any((weights < 0) | (weights > 1)):
        raise ValueError("weights must lie between zero and one")
    err = estimate - truth
    if not np.isfinite(err).all():
        raise ValueError("errors exceed the finite numeric range")
    max_error = float(np.max(np.abs(err)))
    scaled = err / max_error if max_error else err
    return {
        "rmse": max_error * float(np.sqrt(np.mean(scaled * scaled))),
        "mae": max_error * float(np.mean(np.abs(scaled))),
        "max_abs_error": max_error,
        "clipped_fraction": float(np.mean(weights < 0.999999)),
    }


def run_development(
    config: RunConfig, model: LinearGaussianModel | None = None
) -> dict[str, Any]:
    config.validate()
    implementation_sha256 = _checked_source_identity()
    model = model or LinearGaussianModel()
    data = generate_sequence(config, model)
    b0 = filter_sequence(data["observation"], model)
    b1 = filter_sequence(data["observation"], model, huber_c=config.huber_c)
    b2 = aorkf_huber_sequence(data["observation"], model, h=config.ao_h)
    b3 = iorkf_huber_sequence(data["observation"], model, h=config.io_h)
    outputs = {
        "B0_classical": b0,
        "B1_fixed_huber": b1,
        "B2_AO_robkf_huber": b2,
        "B3_IO_robkf_huber": b3,
    }
    trajectories = {key: value.tolist() for key, value in data.items()}
    result = {
        "schema": DEVELOPMENT_RECORD_SCHEMA,
        "evidence_role": "DEVELOPMENT_ONLY",
        "protected_confirmatory_ids": "1000-1029 CLOSED",
        "config": asdict(config),
        "model": asdict(model),
        "seed": _seed(config.experiment_id),
        "generator": {
            "name": "iris_development_scalar_v1",
            "implementation_sha256": implementation_sha256,
            "config_sha256": _digest(
                {"config": asdict(config), "model": asdict(model)}
            ),
            "trajectories_sha256": _digest(trajectories),
            "prng": "numpy.random.PCG64",
            "seed_recipe": "int(sha256('iris-dev:<experiment_id>')[:8], 16)",
            "initial_state": 0.0,
            "scope": (
                "New scalar development inputs; "
                "not recovered canonical IRIS trajectories"
            ),
        },
        "trajectories": trajectories,
        "baseline_outputs": {
            name: {key: value.tolist() for key, value in values.items()}
            for name, values in outputs.items()
        },
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "baseline_provenance": {
            "B0_classical": "scalar Kalman filter in this repository",
            "B1_fixed_huber": "historical IRIS standardized-residual Huber control",
            "B2_AO_robkf_huber": ROBKF_REFERENCE,
            "B3_IO_robkf_huber": ROBKF_REFERENCE,
        },
        "results": {
            "B0_classical": summarize(data["state"], b0["mean"], b0["robust_weight"]),
            "B1_fixed_huber": summarize(data["state"], b1["mean"], b1["robust_weight"]),
            "B2_AO_robkf_huber": summarize(
                data["state"], b2["mean"], b2["robust_weight"]
            ),
            "B3_IO_robkf_huber": summarize(
                data["state"], b3["mean"], b3["robust_weight"]
            ),
        },
    }
    _checked_source_identity()
    return result


def write_result(result: dict[str, Any], path: str) -> None:
    """Publish complete strict JSON without replacing a previous result."""
    payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{destination.name}.", dir=destination.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, destination)
    finally:
        os.unlink(temporary)


def _digest(value: Any) -> str:
    content = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def verify_development_record(record: dict[str, Any]) -> dict[str, Any]:
    """Replay a v2 development record under the exact recorded implementation.

    This verifies engineering reproducibility only. It cannot establish the
    identity of the missing historical canonical corpus or open protected IDs.
    """
    if record.get("schema") != DEVELOPMENT_RECORD_SCHEMA:
        raise ValueError("unsupported development record schema")
    try:
        config = RunConfig(**record["config"])
        model = LinearGaussianModel(**record["model"])
    except (KeyError, TypeError) as exc:
        raise ValueError("invalid development record configuration") from exc
    config.validate()
    model.validate()
    if (
        record.get("generator", {}).get("implementation_sha256")
        != _checked_source_identity()
    ):
        raise ValueError("development record implementation identity differs")
    expected = run_development(config, model)
    for key in (
        "evidence_role",
        "protected_confirmatory_ids",
        "seed",
        "generator",
        "trajectories",
        "baseline_provenance",
        "baseline_outputs",
        "results",
    ):
        if _digest(record.get(key)) != _digest(expected[key]):
            raise ValueError(f"development record {key} failed exact replay")
    return {
        "status": "VERIFIED_DEVELOPMENT_REPLAY",
        "experiment_id": config.experiment_id,
        "scenario": config.scenario,
        "observations": config.length,
        "baselines": len(expected["results"]),
        "canonical_provenance_resolved": False,
    }
