import json

import numpy as np

from rfnode.common.util import NumpyComplexEncoder
from rfnode.model.model import HighPowerFrequency, HighPowerSample


def test_HighPowerSample():
    lst = np.array([1.1 + 0.1j], dtype=np.complex128)
    power = HighPowerSample(50.5, 1050000000, lst)
    str_json = power.to_json(NumpyComplexEncoder)
    assert power.get_power() == 50.5
    assert power.get_frequency() == 1050000000
    str_json = power.to_json(NumpyComplexEncoder)
    assert str_json is not None


def test_HighPowerFrequencies():
    highPowerFrequency = HighPowerFrequency(20.55, [1.5, 1.0])
    str_json = highPowerFrequency.to_json(json.JSONEncoder)
    assert str_json is not None
