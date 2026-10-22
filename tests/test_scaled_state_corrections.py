from decimal import Decimal, localcontext

import numpy as np
import pytest

from iris_baselines import (
    LinearGaussianModel,
    aorkf_huber_sequence,
    filter_sequence,
    iorkf_huber_sequence,
)

FILTERS = [
    pytest.param(filter_sequence, {}, id="B0"),
    pytest.param(filter_sequence, {"huber_c": 1e200}, id="B1-classical-limit"),
    pytest.param(aorkf_huber_sequence, {"h": 1e200}, id="B2-classical-limit"),
    pytest.param(iorkf_huber_sequence, {"h": 1e200}, id="B3-classical-limit"),
]


def _decimal_correction(model, observation):
    with localcontext() as context:
        context.prec = 200
        transition = Decimal.from_float(model.transition)
        predicted = transition**2 * Decimal.from_float(model.initial_var)
        predicted += Decimal.from_float(model.process_var)
        mapping = Decimal.from_float(model.observation)
        variance = mapping**2 * predicted + Decimal.from_float(model.observation_var)
        return float(predicted * mapping * Decimal.from_float(observation) / variance)


@pytest.mark.parametrize("filter_fn,kwargs", FILTERS)
@pytest.mark.parametrize("mapping_sign", [-1.0, 1.0])
@pytest.mark.parametrize("observation_sign", [-1.0, 1.0])
@pytest.mark.parametrize("failure", ["gain-numerator-underflow", "gain-underflow"])
def test_representable_correction_survives_intermediate_underflow(
    filter_fn, kwargs, mapping_sign, observation_sign, failure
):
    if failure == "gain-numerator-underflow":
        model = LinearGaussianModel(
            initial_var=1e-300,
            process_var=1e-300,
            observation_var=1e-300,
            observation=mapping_sign * 1e-100,
        )
        observation = observation_sign
    else:
        model = LinearGaussianModel(
            initial_var=1e-200,
            process_var=1e-200,
            observation_var=1e100,
            observation=mapping_sign * 1e-100,
        )
        observation = observation_sign * 1e100
    expected = _decimal_correction(model, observation)
    assert expected != 0.0
    result = filter_fn(np.array([observation]), model, **kwargs)
    assert result["mean"][0] == pytest.approx(expected, rel=2e-15, abs=0)
    assert result["variance"][0] > 0.0
    assert result["robust_weight"][0] == 1.0


@pytest.mark.parametrize("filter_fn,kwargs", FILTERS)
def test_genuinely_unrepresentable_correction_can_round_to_zero(filter_fn, kwargs):
    model = LinearGaussianModel(
        initial_var=1e-200,
        process_var=1e-200,
        observation_var=1e100,
        observation=1e-100,
    )
    assert _decimal_correction(model, 1.0) == 0.0
    result = filter_fn(np.array([1.0]), model, **kwargs)
    assert result["mean"][0] == 0.0
    assert result["variance"][0] > 0.0


@pytest.mark.parametrize("filter_fn,kwargs", FILTERS)
def test_ordinary_correction_retains_classical_value(filter_fn, kwargs):
    model = LinearGaussianModel()
    result = filter_fn(np.array([0.5]), model, **kwargs)
    assert result["mean"][0] == pytest.approx(
        _decimal_correction(model, 0.5), rel=2e-15
    )


@pytest.mark.parametrize("sign", [-1.0, 1.0])
def test_ao_clips_correction_recovered_from_underflowed_gain_numerator(sign):
    model = LinearGaussianModel(
        initial_var=1e-300,
        process_var=1e-300,
        observation_var=1e-300,
        observation=1e-100,
    )
    result = aorkf_huber_sequence(np.array([sign]), model, h=1e-150)
    assert result["mean"][0] == sign * 1e-150
    assert result["robust_weight"][0] == pytest.approx(5e-51, rel=2e-15, abs=0)


@pytest.mark.parametrize("sign", [-1.0, 1.0])
def test_residual_huber_retains_correction_after_gain_numerator_underflows(sign):
    model = LinearGaussianModel(
        initial_var=1e-300,
        process_var=1e-300,
        observation_var=1e-300,
        observation=1e-100,
    )
    result = filter_sequence(np.array([sign]), model, huber_c=1.0)
    assert result["mean"][0] == pytest.approx(sign * 2e-250, rel=2e-15, abs=0)
    assert result["robust_weight"][0] == pytest.approx(1e-150, rel=2e-15, abs=0)
