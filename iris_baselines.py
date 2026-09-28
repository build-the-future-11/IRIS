from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any
import hashlib
import json
import math
import os
import platform
import sys

import numpy as np

PROTECTED_IDS = set(range(1000, 1030))

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
        if self.process_var <= 0 or self.observation_var <= 0 or self.initial_var <= 0:
            raise ValueError("All variances must be strictly positive")


@dataclass(frozen=True)
class RunConfig:
    experiment_id: int
    scenario: str
    length: int = 200
    huber_c: float = 1.5
    ao_h: float = 2.0
    io_h: float = 2.0

    def validate(self) -> None:
        if self.experiment_id in PROTECTED_IDS:
            raise ValueError(f"Protected confirmatory experiment ID {self.experiment_id} is closed")
        if self.length < 4:
            raise ValueError("length must be >= 4")
        if self.huber_c <= 0:
            raise ValueError("huber_c must be > 0")
        if self.ao_h <= 0:
            raise ValueError("ao_h must be > 0")
        if self.io_h <= 0:
            raise ValueError("io_h must be > 0")
        if self.scenario not in {"clean", "additive_outlier", "persistent_shift", "false_open", "mixed"}:
            raise ValueError(f"Unknown scenario: {self.scenario}")


def _seed(experiment_id: int) -> int:
    return int(hashlib.sha256(f"iris-dev:{experiment_id}".encode()).hexdigest()[:8], 16)


def generate_sequence(config: RunConfig, model: LinearGaussianModel) -> dict[str, np.ndarray]:
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
        x[t] = model.transition * x[t - 1] + drift + rng.normal(0.0, math.sqrt(model.process_var))
    y[:] = model.observation * x + rng.normal(0.0, math.sqrt(model.observation_var), size=config.length)
    if config.scenario in {"additive_outlier", "mixed"}:
        for idx in (config.length // 4, 3 * config.length // 4):
            y[idx] += 8.0 * math.sqrt(model.observation_var)
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
    return value * weight, weight


def _kalman_terms(
    m: float,
    p: float,
    obs: float,
    model: LinearGaussianModel,
) -> tuple[float, float, float, float]:
    m_pred = model.transition * m
    p_pred = model.transition * p * model.transition + model.process_var
    innovation = obs - model.observation * m_pred
    s = model.observation * p_pred * model.observation + model.observation_var
    gain = p_pred * model.observation / s
    return m_pred, p_pred, innovation, gain


def filter_sequence(
    observations: np.ndarray,
    model: LinearGaussianModel,
    *,
    huber_c: float | None = None,
) -> dict[str, np.ndarray]:
    """Classical B0 filter, or the historical IRIS B1 residual-Huber control."""
    model.validate()
    observations = np.asarray(observations, dtype=float)
    if observations.ndim != 1 or observations.size == 0:
        raise ValueError("observations must be a non-empty 1D array")
    if huber_c is not None and huber_c <= 0:
        raise ValueError("huber_c must be > 0")

    means = np.zeros_like(observations)
    variances = np.zeros_like(observations)
    innovations = np.zeros_like(observations)
    standardized = np.zeros_like(observations)
    weights = np.ones_like(observations)

    m = model.initial_mean
    p = model.initial_var
    for t, obs in enumerate(observations):
        m_pred, p_pred, innovation, gain = _kalman_terms(m, p, float(obs), model)
        s = model.observation * p_pred * model.observation + model.observation_var
        z = innovation / math.sqrt(s)
        weight = 1.0 if huber_c is None else _huber_weight(z, huber_c)
        effective_innovation = weight * innovation
        m = m_pred + gain * effective_innovation
        p = (1.0 - gain * model.observation) * p_pred

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
    observations = np.asarray(observations, dtype=float)
    if observations.ndim != 1 or observations.size == 0:
        raise ValueError("observations must be a non-empty 1D array")
    if h <= 0:
        raise ValueError("h must be > 0")
    means = np.zeros_like(observations)
    variances = np.zeros_like(observations)
    innovations = np.zeros_like(observations)
    corrections = np.zeros_like(observations)
    weights = np.ones_like(observations)

    m = model.initial_mean
    p = model.initial_var
    for t, obs in enumerate(observations):
        m_pred, p_pred, innovation, gain = _kalman_terms(m, p, float(obs), model)
        raw_update = gain * innovation
        update, weight = _clip_scalar(raw_update, h)
        m = m_pred + update
        p = (1.0 - gain * model.observation) * p_pred

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
    observations = np.asarray(observations, dtype=float)
    if observations.ndim != 1 or observations.size == 0:
        raise ValueError("observations must be a non-empty 1D array")
    if h <= 0:
        raise ValueError("h must be > 0")

    if model.observation == 0:
        raise ValueError("observation must be non-zero for the scalar IO-robust baseline")

    means = np.zeros_like(observations)
    variances = np.zeros_like(observations)
    innovations = np.zeros_like(observations)
    robust_components = np.zeros_like(observations)
    weights = np.ones_like(observations)

    m = model.initial_mean
    p = model.initial_var
    for t, obs in enumerate(observations):
        m_pred, p_pred, innovation, gain = _kalman_terms(m, p, float(obs), model)
        raw_component = (1.0 - model.observation * gain) * innovation
        robust_component, weight = _clip_scalar(raw_component, h)
        m = m_pred + (innovation - robust_component) / model.observation
        p = (1.0 - gain * model.observation) * p_pred

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


def summarize(truth: np.ndarray, estimate: np.ndarray, weights: np.ndarray) -> dict[str, float]:
    err = np.asarray(estimate) - np.asarray(truth)
    return {
        "rmse": float(np.sqrt(np.mean(err * err))),
        "mae": float(np.mean(np.abs(err))),
        "max_abs_error": float(np.max(np.abs(err))),
        "clipped_fraction": float(np.mean(np.asarray(weights) < 0.999999)),
    }


def run_development(config: RunConfig, model: LinearGaussianModel | None = None) -> dict[str, Any]:
    config.validate()
    model = model or LinearGaussianModel()
    data = generate_sequence(config, model)
    b0 = filter_sequence(data["observation"], model)
    b1 = filter_sequence(data["observation"], model, huber_c=config.huber_c)
    b2 = aorkf_huber_sequence(data["observation"], model, h=config.ao_h)
    b3 = iorkf_huber_sequence(data["observation"], model, h=config.io_h)
    return {
        "evidence_role": "DEVELOPMENT_ONLY",
        "protected_confirmatory_ids": "1000-1029 CLOSED",
        "config": asdict(config),
        "model": asdict(model),
        "seed": _seed(config.experiment_id),
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
            "B2_AO_robkf_huber": summarize(data["state"], b2["mean"], b2["robust_weight"]),
            "B3_IO_robkf_huber": summarize(data["state"], b3["mean"], b3["robust_weight"]),
        },
    }


def write_result(result: dict[str, Any], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
