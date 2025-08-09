import json

"""
{
  "freq_start":"103.5",
  "freq_end":"109.5",
  "freq_step":"100",
  "sample_size":"1024",
  "sample_rate":"3.2",
  "power_threshold":"20.00",
  "rf_sender_port":"ttyACM0",
  "rf_sender_port_windows":"COM3",
  "rf_sleep_time": "0.1"
}
"""


class Setting:
    freq_start: float = 103.5
    freq_end: float = 109.5
    freq_step: int = 100
    sample_size: int = 1024
    power_threshold: float = 20.00
    rf_sender_port: str = "ttyACM0"
    fr_sender_port_windows: str = "COM3"
    rf_sleep_time: float = 0.1

    @staticmethod
    def load_setting(file: str):
        with open(file) as f:
            config = json.load(f)
            Setting.freq_start = int(float(config["freq_start"]) * 1e6)  # from MHz to Hz
            Setting.freq_end = int(float(config["freq_end"]) * 1e6)  # from MHz to Hz
            Setting.freq_step = int(float(config["freq_step"]) * 1e3)  # from KHz to Hz
            Setting.sample_size = int(config["sample_size"])
            Setting.sample_rate = int(float(config["sample_rate"]) * 1e6)  # from MHz to Hz
            Setting.power_threshold = float(config["power_threshold"])  # 56.0 dbm
            Setting.rf_sender_port = str(config["rf_sender_port"])
            Setting.rf_sender_port_windows = str(config["rf_sender_port_windows"])
            Setting.rf_sleep_time = float(config["rf_sleep_time"])


if __name__ == "__main__":
    import os.path
    from pathlib import Path

    s = os.path.dirname(__file__)
    p = Path(s).parents[1]
    raw_path = str(p) + os.path.sep + "setting.json"
    Setting.load_setting(raw_path)
    print(Setting.freq_start)
    print(Setting.freq_end)
    print(Setting.freq_step)
    print(Setting.sample_size)
    print(Setting.sample_rate)
    print(Setting.power_threshold)
    print(Setting.rf_sender_port)
    print(Setting.rf_sender_port_windows)
    print(Setting.rf_sleep_time)
