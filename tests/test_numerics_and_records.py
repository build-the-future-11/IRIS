import json
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal, localcontext

import numpy as np
import pytest

from iris_baselines import (
    LinearGaussianModel,
    RunConfig,
    aorkf_huber_sequence,
    filter_sequence,
    iorkf_huber_sequence,
    run_development,
    summarize,
    verify_development_record,
    write_result,
)

FILTERS = (filter_sequence, aorkf_huber_sequence, iorkf_huber_sequence)


@pytest.mark.parametrize("value", ["1000", 1000.5, True, -1, np.nan])
def test_experiment_identity_cannot_be_coerced_around_protected_boundary(value):
    with pytest.raises(ValueError, match="experiment_id"):
        run_development(RunConfig(experiment_id=value, scenario="clean"))


@pytest.mark.parametrize("experiment_id", range(1000, 1030))
def test_every_protected_id_is_rejected_before_generator(monkeypatch, experiment_id):
    def forbidden(*args, **kwargs):
        pytest.fail("generator was entered for a protected ID")

    monkeypatch.setattr(np.random, "default_rng", forbidden)
    with pytest.raises(ValueError, match="Protected confirmatory"):
        run_development(RunConfig(experiment_id=experiment_id, scenario="clean"))


@pytest.mark.parametrize(
    "name",
    [
        "transition",
        "observation",
        "process_var",
        "observation_var",
        "initial_mean",
        "initial_var",
    ],
)
@pytest.mark.parametrize("value", [np.nan, np.inf, True])
def test_all_model_parameters_require_finite_real_values(name, value):
    with pytest.raises(ValueError, match=name):
        replace(LinearGaussianModel(), **{name: value}).validate()


@pytest.mark.parametrize("filter_fn", FILTERS)
@pytest.mark.parametrize(
    "values", [[np.nan], [np.inf], [1 + 2j], [True], ["1"], [[1.0]]]
)
def test_filters_reject_lossy_or_nonfinite_observations(filter_fn, values):
    with pytest.raises(ValueError, match="observations"):
        filter_fn(np.asarray(values), LinearGaussianModel())


@pytest.mark.parametrize("name", ["huber_c", "ao_h", "io_h"])
@pytest.mark.parametrize("value", [np.nan, np.inf, 0, True])
def test_nonfinite_or_ambiguous_thresholds_fail_before_execution(name, value):
    with pytest.raises(ValueError, match=name):
        run_development(replace(RunConfig(41, "clean"), **{name: value}))


@pytest.mark.parametrize("filter_fn", FILTERS)
def test_posterior_variance_survives_gain_rounding_to_one(filter_fn):
    model = LinearGaussianModel(initial_var=1e20, observation_var=0.25)
    result = filter_fn(np.array([0.0]), model)
    with localcontext() as context:
        context.prec = 60
        p = Decimal("1e20") + Decimal("0.05")
        expected = float(p * Decimal("0.25") / (p + Decimal("0.25")))
    assert result["variance"][0] == pytest.approx(expected, rel=1e-15)
    assert result["variance"][0] > 0


def test_io_unclipped_limit_does_not_cancel_for_tiny_observation_map():
    model = LinearGaussianModel(observation=1e-12)
    observations = np.array([1.0, -0.5, 0.25])
    classical = filter_sequence(observations, model)
    io = iorkf_huber_sequence(observations, model, h=1e12)
    np.testing.assert_array_equal(io["mean"], classical["mean"])
    assert np.any(classical["mean"] != 0)


def test_metric_norm_is_stable_when_finite_errors_would_overflow_on_squaring():
    result = summarize(np.zeros(2), np.array([1e200, -1e200]), np.ones(2))
    assert result["rmse"] == pytest.approx(1e200)
    assert result["mae"] == pytest.approx(1e200)


def test_metrics_reject_accidental_numpy_broadcasting():
    with pytest.raises(ValueError, match="identical shapes"):
        summarize(np.zeros(3), np.ones(1), np.ones(3))


def test_complete_record_roundtrips_and_replays_all_four_baselines(tmp_path):
    result = run_development(RunConfig(41, "mixed", length=32))
    output = tmp_path / "result.json"
    write_result(result, str(output))
    stored = json.loads(output.read_text())
    assert len(stored["trajectories"]["state"]) == 32
    assert verify_development_record(stored) == {
        "status": "VERIFIED_DEVELOPMENT_REPLAY",
        "experiment_id": 41,
        "scenario": "mixed",
        "observations": 32,
        "baselines": 4,
        "canonical_provenance_resolved": False,
    }


@pytest.mark.parametrize("target", ["trajectory", "filter", "metric", "source", "seed"])
def test_record_replay_rejects_tampering(target):
    record = deepcopy(run_development(RunConfig(42, "clean", length=16)))
    if target == "trajectory":
        record["trajectories"]["state"][2] += 1
    elif target == "filter":
        record["baseline_outputs"]["B2_AO_robkf_huber"]["mean"][2] += 1
    elif target == "metric":
        record["results"]["B0_classical"]["rmse"] += 1
    elif target == "source":
        record["generator"]["implementation_sha256"] = "0" * 64
    else:
        record["seed"] += 1
    with pytest.raises(ValueError):
        verify_development_record(record)


def test_publishing_never_overwrites_existing_evidence(tmp_path):
    output = tmp_path / "evidence.json"
    output.write_text("previous evidence\n")
    with pytest.raises(FileExistsError):
        write_result({"new": True}, str(output))
    assert output.read_text() == "previous evidence\n"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["evidence.json"]


def test_nonfinite_output_cannot_create_an_artifact(tmp_path):
    output = tmp_path / "new" / "result.json"
    with pytest.raises(ValueError):
        write_result({"rmse": float("nan")}, str(output))
    assert not output.parent.exists()
