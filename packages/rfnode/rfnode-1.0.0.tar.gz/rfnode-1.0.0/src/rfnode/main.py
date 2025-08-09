import argparse
import platform

from rtlsdr import RtlSdr
from serial import Serial

from rfnode.broker import DataBroker
from rfnode.common.log_manager import LogManager
from rfnode.common.setting import Setting
from rfnode.common.util import Util
from rfnode.devicemanager import DeviceManager
from rfnode.scanner import Scanner
from rfnode.sender.sender import Sender

"""
A- Make the project in edit mode
$ pwd
/home/alan/workspace-python/RTL-SDR/rf-surveillance
$ pip install -e .
$ rfnode setting.json -vvv -ld /home/alan/tmp

//////////////////////////////////////////

B- Using PYTHONPATH (Not recommended)
Linux:
=====
$ export PYTHONPATH=/home/alan/workspace-python/RTL-SDR/rf-surveillance/src
$ pwd
 /home/alan/workspace-python/RTL-SDR/rf-surveillance/src
$ python rfnode setting.json -vvv -ld /home/alan/tmp

Windows:
========
set PYTHONPATH=/home/alan/workspace-python/RTL-SDR/rf-surveillance/src
echo %PYTHONPATH%
python rfnode setting.json -vvv -ld /home/alan/tmp
Note: Check the devicemanager from the control panel for the port name
"""


def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument("setting", help="path to setting file", type=str, metavar="file")
    parser.add_argument(
        "-ld",
        "--log_directory",
        help="store output log in a directory",
        type=str,
        metavar="dir",
    )
    parser.add_argument("-v", "--verbose", action="count", default=0)
    args = parser.parse_args()

    LogManager().config_logger(args.verbose, args.log_directory)
    Setting.load_setting(args.setting)

    data_broker = DataBroker()

    port: str = ""
    if platform.system() == "Windows":
        port = Setting.rf_sender_port_windows
    else:
        port = "/dev/" + Setting.rf_sender_port

    ser = Serial(port=port, baudrate=115200)
    sender: Sender = Sender(ser, hold=Setting.rf_sleep_time)
    data_broker.set_rf_sender(sender)

    data_broker.start()

    serial_numbers = DeviceManager.get_device_serial_list()
    frequencies = Util.generate_array(
        Setting.freq_start, Setting.freq_end, Setting.freq_step, len(serial_numbers)
    )
    print(f"RTL SDR numbers {len(serial_numbers)}")

    scanners = []  # a list of scanner

    for i in range(len(serial_numbers)):
        print(f"device index {i}")
        # see https://pyrtlsdr.readthedocs.io/en/latest/rtlsdr.html
        sdr = RtlSdr(device_index=i)
        print(f"Sample rate in millions(Msps) {Setting.sample_rate/1e6}")
        sdr.set_sample_rate(
            Setting.sample_rate
        )  # default sample_rate value used on initialization: 1.024e6 (1024 Msps)
        print(f"IQ sample size(ex: 0.7 -1.5j) {Setting.sample_size}\n\n")
        scanner = Scanner(
            frequencies=frequencies[i],
            sample_size=Setting.sample_size,
            power_threshold=Setting.power_threshold,
            sdr=sdr,
        )
        scanners.append(scanner)

    print(f"Number of threads: {len(scanners)}\n\n")
    for scanner in scanners:
        scanner.start()

    for thread in scanners:
        thread.join()
        print(f"Thread {thread.name} is finished now")

    # Block until all tasks are done
    print("Before the join for queue ...")
    DataBroker.q.join()
    print("All work completed")


# this is important so that it does not run from pytest
if __name__ == "__main__":
    main()
