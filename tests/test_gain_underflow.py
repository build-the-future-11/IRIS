"""Analytic scalar gain cases whose product underflows before division."""

from decimal import Decimal, localcontext

import numpy as np
import pytest

from iris_baselines import (
    LinearGaussianModel,
    _kalman_terms,
    aorkf_huber_sequence,
    filter_sequence,
)


@pytest.mark.parametrize("observation", [1e-100, -1e-100])
def test_gain_keeps_representable_value_after_subnormal_product(observation):
    model = LinearGaussianModel(
        transition=0,
        observation=observation,
        process_var=1e-300,
        observation_var=1e-300,
    )
    _, p, _, gain, s = _kalman_terms(0, 1, 1e100, model)
    with localcontext() as context:
        context.prec = 100
        reference = float(Decimal(str(p)) * Decimal(str(observation)) / Decimal(str(s)))
    assert gain == pytest.approx(reference, rel=1e-14, abs=0)


@pytest.mark.parametrize("huber", [None, 1e300])
def test_unclipped_filter_keeps_nonzero_mean_correction(huber):
    model = LinearGaussianModel(
        transition=0, observation=1e-100, process_var=1e-300, observation_var=1e-300
    )
    result = filter_sequence(np.array([1e100]), model, huber_c=huber)
    assert result["mean"][0] == pytest.approx(1.0, rel=1e-14)
    assert result["variance"][0] == pytest.approx(1e-300, rel=1e-14, abs=0)


def test_ao_control_clips_the_preserved_correction():
    model = LinearGaussianModel(
        transition=0, observation=1e-100, process_var=1e-300, observation_var=1e-300
    )
    result = aorkf_huber_sequence(np.array([1e100]), model, h=0.5)
    assert result["mean"][0] == 0.5
    assert result["robust_weight"][0] == pytest.approx(0.5)
