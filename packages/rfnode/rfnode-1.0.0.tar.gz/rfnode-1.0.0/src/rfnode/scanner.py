# scan module  talk more
import logging
from threading import Thread

import numpy as np
from rtlsdr import RtlSdr

from rfnode.broker import DataBroker
from rfnode.devicemanager import DeviceManager
from rfnode.model.model import HighPowerFrequency, HighPowerSample


def display_menu():
    print(
        """
    ##################################
    #                                #
    #      RTL SDR NODE SCANNER      #
    #                                #
    ##################################

    """
    )


class Scanner(Thread):

    def __init__(
        self,
        frequencies: list[np.int64],
        sample_size: int,
        power_threshold: float,
        sdr: RtlSdr,
    ):
        Thread.__init__(self)
        self.frequencies = frequencies
        self.sample_size = sample_size
        self.power_threshold = power_threshold
        self.sdr = sdr

        self.logger = logging.getLogger("Scanner")

    def run(self):
        self.logger.info(f"{self.name}: Starting scanner")

        stop_freq = self.frequencies[len(self.frequencies) - 1]
        start_freq = self.frequencies[0]
        print(f"start freq(MHz) {start_freq/1e6} -->{self.getName()}")
        print(f"stop_freq(MHz) {stop_freq/1e6} -->{self.getName()}")
        self.logger.info(
            f"{self.name:} Scanning from {self.frequencies[0]/1e6} MHz to {stop_freq/1e6} MHz..."
        )
        counter = 0
        print("\n")
        while True:
            counter += 1
            print(f"SCANNING-->iteration:{counter} -->{self.getName()}")
            print("\n\n")
            self.do_run()

        self.sdr.close()

    def do_run(self) -> None:
        power_levels = []
        for freq in self.frequencies:
            self.sdr.center_freq = freq
            # DEFAULT_READ_SIZE = 1024
            samples = self.sdr.read_samples(self.sample_size)
            spectrum = np.fft.fftshift(np.abs(np.fft.fft(samples)) ** 2)
            power = 10 * np.log10(np.mean(spectrum))
            if power > self.power_threshold:  # configure the power to send the sample
                self.logger.info(f"{self.name:} freq is {freq} power is {power}")
                high_power_sample = HighPowerSample(power, freq / 1e6, samples)
                DataBroker.q.put(
                    high_power_sample
                )  # sending the samples for config threshold power
        power_levels.append(power)
        threshold = np.mean(power_levels) + np.std(power_levels)
        high_power_indices = np.where(np.array(power_levels) > threshold)[
            0
        ]  # tuple (np.array(),)
        high_power_freqs = (
            self.frequencies[high_power_indices] / 1e6
        )  # numpy array sending array of indices  into a np array
        self.logger.info(
            f"{self.name}: High Power frequencies detected at (MHz): {high_power_freqs}"
        )
        self.logger.info(f"{self.name}: Sending the result to the queue")
        high_power_freqs = HighPowerFrequency(threshold, high_power_freqs)
        DataBroker.q.put(
            high_power_freqs
        )  # send frequencies with high power exceeding threshold


if __name__ == "__main__":
    serial_numbers = DeviceManager.get_device_serial_list()
    print(f" RTL SDR numbers {len(serial_numbers)}")

    params = {}
    level = logging.INFO
    params["format"] = "[%(asctime)s][%(levelname)7s][%(name)6s] %(message)s"
    params["level"] = level
    params["datefmt"] = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(**params)

    data_broker = DataBroker()
    data_broker.start()

    scanners = []  # a list of scanner
    arrs = np.arange(105 * 1e6, 106 * 1e6, 10000)
    frequencies = np.split(arrs, len(serial_numbers))
    for i in range(len(serial_numbers)):
        print(f"device index {i}")
        sdr = RtlSdr(device_index=i)
        sample_size = 1024 * 1024
        sample_rate = 32 * 1e5  # 3.2 MHz
        power_threshold = 55.55
        scanner = Scanner(
            frequencies=frequencies[i],
            sample_rate=sample_rate,
            sample_size=sample_size,
            power_threshold=power_threshold,
            sdr=sdr,
        )

        scanners.append(scanner)

    for scanner in scanners:
        scanner.start()

    print(f"Started number of threads: {len(scanners)}")
    for thread in scanners:
        print("waiting for the thread " + thread.name + " to finish")
        thread.join()
