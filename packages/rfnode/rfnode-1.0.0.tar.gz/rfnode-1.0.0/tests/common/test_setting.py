import os.path
from pathlib import Path

from rfnode.common.setting import Setting


def test_setting():
    s = os.path.dirname(__file__)
    p = Path(s).parents[1]
    raw_path = str(p) + os.path.sep + "src" + os.path.sep + "setting.json"
    Setting.load_setting(raw_path)
    assert Setting.freq_start == 100500000
    assert Setting.freq_end == 109500000
    assert Setting.freq_step == 100000
    assert Setting.sample_size == 1024
    assert Setting.sample_rate == 1024000
    assert Setting.power_threshold == 20.0
    assert Setting.rf_sender_port == "ttyACM0"
    assert Setting.rf_sender_port_windows == "COM3"
    assert Setting.rf_sleep_time == 0.1
