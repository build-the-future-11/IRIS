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

    def validate(self) -> None:
        if self.experiment_id in PROTECTED_IDS:
            raise ValueError(f"Protected confirmatory experiment ID {self.experiment_id} is closed")
        if self.length < 4:
            raise ValueError("length must be >= 4")
        if self.huber_c <= 0:
            raise ValueError("huber_c must be > 0")
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


def filter_sequence(observations: np.ndarray, model: LinearGaussianModel, *, huber_c: float | None = None) -> dict[str, np.ndarray]:
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
        m_pred = model.transition * m
        p_pred = model.transition * p * model.transition + model.process_var
        innovation = obs - model.observation * m_pred
        s = model.observation * p_pred * model.observation + model.observation_var
        z = innovation / math.sqrt(s)
        weight = 1.0 if huber_c is None else _huber_weight(z, huber_c)
        effective_innovation = weight * innovation
        k = p_pred * model.observation / s
        m = m_pred + k * effective_innovation
        p = (1.0 - k * model.observation) * p_pred

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
        "results": {
            "B0_classical": summarize(data["state"], b0["mean"], b0["robust_weight"]),
            "B1_fixed_huber": summarize(data["state"], b1["mean"], b1["robust_weight"]),
        },
    }


def write_result(result: dict[str, Any], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
