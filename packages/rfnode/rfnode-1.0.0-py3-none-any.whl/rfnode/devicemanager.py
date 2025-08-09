""" Device Manager works as a discovery for plug and play 
to find the ports of the attached devices 
"""
import subprocess

from rtlsdr import RtlSdr


class DeviceManager:

    TTYUSB = "ttyUSB"

    def __init__(self):
        pass

    @staticmethod
    def get_device_serial_list() -> list[str]:
        # Get  a list of detected device serial numbers
        # Alan make some check and exception throwing later on
        serial_numbers = RtlSdr.get_device_serial_addresses()
        return serial_numbers

    @staticmethod
    def get_telemetary_device_path() -> str:
        """
        Obtain the telemetary serial path such as /dev/ttyUSB0 or /dev/ttyUSB1
        $ ls -l /dev/serial/by-id
         ... usb-FT231X_USB_UART_D30EZ3WR-if00-port0 -> ../../ttyUSB0
         ... usb-FTDI_FT231X_USB_UART_D30EZ7O4-if00-port0 -> ../../ttyUSB0
        """
        result = subprocess.run(["ls", "-l", "/dev/serial/by-id"], stdout=subprocess.PIPE)
        s = result.stdout.decode()
        lst = s.split("\n")

        for ss in lst:
            device_path: str = None
            if ss.find(DeviceManager.TTYUSB) != -1:
                lst2 = ss.split("->")
                device_path = DeviceManager.__do_get_telemetary_device_path(lst2)
                break
        return device_path

    @staticmethod
    def __do_get_telemetary_device_path(lst2: list) -> str:
        i = lst2[1].find(DeviceManager.TTYUSB)
        if i != -1:
            ttyUSB = lst2[1]
            return ttyUSB[i : len(ttyUSB)]
        else:
            return None


if __name__ == "__main__":
    serial_device_path: str = DeviceManager.get_telemetary_device_path()
    print(serial_device_path)
