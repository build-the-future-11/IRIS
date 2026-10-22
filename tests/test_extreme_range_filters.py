from decimal import Decimal, localcontext

import numpy as np
import pytest

from iris_baselines import (
    LinearGaussianModel,
    aorkf_huber_sequence,
    filter_sequence,
    iorkf_huber_sequence,
)


@pytest.mark.parametrize(
    "filter_fn", [filter_sequence, aorkf_huber_sequence, iorkf_huber_sequence]
)
def test_representable_posterior_survives_underflow_of_noise_fraction(filter_fn):
    model = LinearGaussianModel(
        initial_var=1e100, process_var=1e-100, observation_var=1e-250
    )
    actual = filter_fn(np.array([0.0]), model)["variance"][0]
    with localcontext() as context:
        context.prec = 100
        predicted = Decimal("1e100") + Decimal("1e-100")
        noise = Decimal("1e-250")
        expected = float(predicted * noise / (predicted + noise))
    assert actual == pytest.approx(expected, rel=2e-15, abs=0)
    assert actual > 0


@pytest.mark.parametrize("observation", [1e300, -1e300])
def test_ao_clipping_keeps_threshold_when_multiplicative_weight_underflows(observation):
    threshold = 1e-300
    result = aorkf_huber_sequence(
        np.array([observation]), LinearGaussianModel(), h=threshold
    )
    expected = np.copysign(threshold, observation)
    assert result["robust_component"][0] == expected
    assert result["mean"][0] == expected


@pytest.mark.parametrize("observation", [1e300, -1e300])
def test_residual_huber_keeps_finite_clipped_update_when_weight_underflows(observation):
    model = LinearGaussianModel(initial_var=1.0, process_var=1.0, observation_var=1.0)
    result = filter_sequence(np.array([observation]), model, huber_c=1e-300)
    with localcontext() as context:
        context.prec = 100
        expected = float(
            Decimal(2) / Decimal(3) * Decimal(3).sqrt() * Decimal("1e-300")
        )
    assert result["mean"][0] == pytest.approx(
        np.copysign(expected, observation), rel=2e-15, abs=0
    )


@pytest.mark.parametrize("observation", [1e200, -1e200])
def test_io_retains_residual_component_when_noise_fraction_underflows(observation):
    model = LinearGaussianModel(
        initial_var=1e200, process_var=1e-200, observation_var=1e-200
    )
    result = iorkf_huber_sequence(np.array([observation]), model, h=1e-250)
    assert result["robust_component"][0] == np.copysign(1e-250, observation)
    assert result["variance"][0] == pytest.approx(1e-200, rel=2e-15, abs=0)


@pytest.mark.parametrize(
    "filter_fn", [filter_sequence, aorkf_huber_sequence, iorkf_huber_sequence]
)
def test_mathematically_unrepresentable_posterior_still_fails_explicitly(filter_fn):
    model = LinearGaussianModel(observation=1e100, observation_var=1e-200)
    with pytest.raises(ValueError, match="posterior variance"):
        filter_fn(np.array([0.0]), model)
