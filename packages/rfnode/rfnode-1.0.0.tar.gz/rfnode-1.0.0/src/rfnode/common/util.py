import json

import numpy as np


class Util:

    def __init__(self):
        pass

    @classmethod
    def generate_array(
        cls, freq_start: int, freq_end: int, freq_step: int, device_amount: int
    ) -> list[np.int64]:
        frequencies = np.arange(freq_start, freq_end, freq_step, np.int64)
        return np.array_split(frequencies, device_amount)  # split of equal or near-equal size


class NumpyComplexEncoder(json.JSONEncoder):

    def default(self, obj) -> any:

        if isinstance(obj, complex):
            return (obj.real, obj.imag)
        else:
            return None


if __name__ == "__main__":
    arrs = Util.generate_array(1, 500, 10, 2)
    print(len(arrs))
    print(len(arrs[0]))
    print(len(arrs[1]))
    for arr in arrs:
        for i in arr:
            print(i)
