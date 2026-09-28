import numpy as np
import pytest

from iris_baselines import (
    LinearGaussianModel,
    RunConfig,
    aorkf_huber_sequence,
    filter_sequence,
    generate_sequence,
    iorkf_huber_sequence,
    run_development,
)


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


def test_robkf_ao_and_io_converge_to_classical_when_h_is_infinite():
    obs = np.array([0.1, 0.2, -0.1, 0.3, 0.0], dtype=float)
    model = LinearGaussianModel()
    classical = filter_sequence(obs, model)
    ao = aorkf_huber_sequence(obs, model, h=1e12)
    io = iorkf_huber_sequence(obs, model, h=1e12)

    for robust in (ao, io):
        assert np.allclose(classical["mean"], robust["mean"], atol=1e-12, rtol=0)
        assert np.allclose(classical["variance"], robust["variance"], atol=1e-12, rtol=0)


def test_robkf_ao_clips_state_correction_exactly_in_scalar_case():
    obs = np.array([10.0], dtype=float)
    model = LinearGaussianModel()
    ao = aorkf_huber_sequence(obs, model, h=2.0)

    # RobKF AORKF_huber clips K*innovation itself. Here the ordinary
    # correction is >2, so the one-dimensional norm clip is exactly +2.
    assert ao["mean"][0] == pytest.approx(2.0)
    assert ao["robust_component"][0] == pytest.approx(2.0)
    assert ao["robust_weight"][0] < 1.0


def test_robkf_io_treats_large_observation_as_possible_state_innovation():
    obs = np.array([10.0], dtype=float)
    model = LinearGaussianModel()
    classical = filter_sequence(obs, model)
    ao = aorkf_huber_sequence(obs, model, h=1.0)
    io = iorkf_huber_sequence(obs, model, h=1.0)

    # With a tight threshold, AO suppresses the state correction while IO
    # suppresses the component interpreted as measurement error and therefore
    # follows a plausible latent innovation much more aggressively.
    assert ao["mean"][0] == pytest.approx(1.0)
    assert io["mean"][0] == pytest.approx(9.0)
    assert abs(io["mean"][0] - obs[0]) < abs(classical["mean"][0] - obs[0])
    assert ao["robust_weight"][0] < 1.0
    assert io["robust_weight"][0] < 1.0


def test_result_manifest_is_development_only_and_complete():
    result = run_development(RunConfig(experiment_id=31, scenario="additive_outlier", length=80))
    assert result["evidence_role"] == "DEVELOPMENT_ONLY"
    assert result["protected_confirmatory_ids"] == "1000-1029 CLOSED"
    assert set(result["results"]) == {
        "B0_classical",
        "B1_fixed_huber",
        "B2_AO_robkf_huber",
        "B3_IO_robkf_huber",
    }
    assert result["baseline_provenance"]["B2_AO_robkf_huber"]["commit"] == (
        "0c4287545034bace38b1e8fb795726add61032b5"
    )
    assert result["baseline_provenance"]["B3_IO_robkf_huber"]["commit"] == (
        "0c4287545034bace38b1e8fb795726add61032b5"
    )
    for metrics in result["results"].values():
        assert set(metrics) == {"rmse", "mae", "max_abs_error", "clipped_fraction"}
        assert all(np.isfinite(v) for v in metrics.values())


def test_zero_observation_map_is_rejected_only_by_io_baseline():
    obs = np.array([0.0, 0.1, -0.2], dtype=float)
    model = LinearGaussianModel(observation=0.0)

    # B0/B1/B2 do not require C^{-1}; preserve their prior model domain.
    filter_sequence(obs, model)
    aorkf_huber_sequence(obs, model, h=2.0)

    with pytest.raises(ValueError, match="non-zero"):
        iorkf_huber_sequence(obs, model, h=2.0)
