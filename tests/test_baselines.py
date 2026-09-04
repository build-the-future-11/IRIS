import numpy as np
import pytest

from iris_baselines import LinearGaussianModel, RunConfig, filter_sequence, generate_sequence, run_development


def test_protected_confirmatory_ids_fail_closed():
    with pytest.raises(ValueError, match="Protected confirmatory"):
        run_development(RunConfig(experiment_id=1000, scenario="clean"))


def test_development_generation_is_deterministic():
    cfg = RunConfig(experiment_id=17, scenario="mixed", length=64)
    a = generate_sequence(cfg, LinearGaussianModel())
    b = generate_sequence(cfg, LinearGaussianModel())
    assert np.array_equal(a["state"], b["state"])
    assert np.array_equal(a["observation"], b["observation"])


def test_huber_converges_to_classical_when_threshold_is_effectively_infinite():
    obs = np.array([0.1, 0.2, -0.1, 0.3, 0.0], dtype=float)
    model = LinearGaussianModel()
    classical = filter_sequence(obs, model)
    robust = filter_sequence(obs, model, huber_c=1e12)
    assert np.allclose(classical["mean"], robust["mean"], atol=1e-12, rtol=0)
    assert np.allclose(classical["variance"], robust["variance"], atol=1e-12, rtol=0)


def test_huber_clips_large_measurement_outlier():
    obs = np.array([0.0, 0.0, 15.0, 0.0, 0.0], dtype=float)
    model = LinearGaussianModel(observation_var=0.25)
    classical = filter_sequence(obs, model)
    robust = filter_sequence(obs, model, huber_c=1.5)
    assert robust["robust_weight"][2] < 1.0
    assert abs(robust["mean"][2]) < abs(classical["mean"][2])


def test_result_manifest_is_development_only_and_complete():
    result = run_development(RunConfig(experiment_id=31, scenario="additive_outlier", length=80))
    assert result["evidence_role"] == "DEVELOPMENT_ONLY"
    assert result["protected_confirmatory_ids"] == "1000-1029 CLOSED"
    assert set(result["results"]) == {"B0_classical", "B1_fixed_huber"}
    for metrics in result["results"].values():
        assert set(metrics) == {"rmse", "mae", "max_abs_error", "clipped_fraction"}
        assert all(np.isfinite(v) for v in metrics.values())
