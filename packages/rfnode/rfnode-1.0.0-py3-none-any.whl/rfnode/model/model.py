"""
{
   "threshold_power": "50.725530686401925",
   "now": "2025-04-06 15:42:10.602488",
   "frequencies": "[104.9]"
}

{
  "threshold_power": "59.2375742505707",
  "now": "2025-04-06 15:42:10.604455",
  "frequencies": "[105.0]"
}



{
   "power": "58.05980129674052", "center_frequency": "105300000",
   "now": "2025-04-06 15:42:10.604455",
   "samples": "[[-0.2784313725490196, -0.05882352941176472],
              [0.0117647058823529, -0.04313725490196085],
              [0.027450980392156765, -0.050980392156862786],
              [0.04313725490196085, 0.07450980392156858],
              ...
              ...
              ...
              ]

}

"""

import json
from datetime import datetime

import numpy as np

from rfnode.common.util import NumpyComplexEncoder


class HighPowerSample:
    def __init__(self, power: float, center_frequency: int, samples: np.ndarray):
        """
        power: The center frequency power which exceeds or equals the thresholder
        center_frequency: The center frequency in Hz
        samples: the taken samples given sample rates in the settings
        """
        self.power = power
        self.center_frequency = center_frequency
        self.samples = samples
        self.date_time = datetime.now()

    def get_frequency(self) -> float:
        return self.center_frequency

    def get_power(self) -> float:
        return self.power

    def to_json(self, clazz=type[NumpyComplexEncoder]) -> str:
        json_str: str = json.dumps(self.samples.tolist(), cls=clazz)
        feq: str = str(self.center_frequency)
        d: dict = {
            "power": str(self.power),
            "center_frequency": feq,
            "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "samples": json_str,
        }
        return json.dumps(d)


class HighPowerFrequency:
    def __init__(self, threshold_power: float, frequencies: list[float]):
        """
        threshold_power: the power in dBm or our power threshold
            The threshold = np.mean(power_levels) + np.std(power_levels)
            dBm = 1.0 milliwatt
            the threshold power which is calcualted by above formula
            each frequency is picked to exceed this power is being selected into a list

        frequencies which have high power over the average
        see Scanner for calculation of the power array
        """
        self.threshold_power = threshold_power
        self.frequencies = frequencies
        self.date_time = datetime.now()

    def to_json(self, clazz=type[json.JSONEncoder]) -> str:
        frequencies_str = json.dumps(self.frequencies, cls=clazz)
        d: dict = {
            "threshold_power": str(self.threshold_power),
            "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "frequencies": frequencies_str,
        }
        return json.dumps(d)


if __name__ == "__main__":
    lst = np.array([1.1 + 0.1j], dtype=np.complex128)
    hightPowerSample = HighPowerSample(50.5, 1050000000, lst)
    str_json = hightPowerSample.to_json(NumpyComplexEncoder)
    print(str_json)

    highPowerFrequency = HighPowerFrequency(20.55, [1.5, 1.0])
    str_json = highPowerFrequency.to_json(json.JSONEncoder)
    print(str_json)
