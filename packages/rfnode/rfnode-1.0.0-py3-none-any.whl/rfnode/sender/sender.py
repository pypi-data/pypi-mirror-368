import struct
import time
import zlib

from serial import Serial


class Sender:
    MAX_PAYLOAD = 32  # max payload size this can change later OK Alan
    NEW_LINE = b"\n"

    def __init__(self, ser: Serial, hold: float = 0.1) -> None:
        self.hold = hold
        self.ser = ser

    def checksum_calculator(self, data: bytes) -> int:
        checksum = zlib.crc32(data)
        return checksum

    # 4bytes*1  = 4 bytes
    def generate_header(self, data: bytes) -> bytes:
        checksum: int = self.checksum_calculator(data)
        return struct.pack("!I", checksum)

    def build_packets(self, payload: str) -> list[bytes]:
        data: bytes = payload.encode() + Sender.NEW_LINE
        header: bytes = self.generate_header(data)
        # Split data into chunks
        chunks = [
            data[i : i + Sender.MAX_PAYLOAD - 2]
            for i in range(0, len(data), Sender.MAX_PAYLOAD - 2)
        ]
        indexed_chunks: list[bytes] = []
        for i, chunk in enumerate(chunks):
            packet = bytes([i]) + chunk  # Add packet index
            indexed_chunks.append(packet)
            # index:int = packet[0]

        indexed_chunks.insert(0, header)  # header at start of the list
        return indexed_chunks

    def send(self, payload: str) -> None:
        packets: list[bytes] = self.build_packets(payload=payload)
        # FIXME Exception can SerialTimeoutException Alan configure for timeout
        for packet in packets:
            self.ser.write(packet)
            # self.ser.flush() # Flush of file like objects. In this case, wait until all data is written.
            time.sleep(self.hold)


def main() -> None:
    ser = Serial("COM3", baudrate=115200)
    sender: Sender = Sender(ser)
    while True:
        # Alan 8*30 = 240bytes + 4 bytes header = 244 bytes is the max
        # payload:str ="This is a large data payload that needs to be split into.This is a large data payload that needs to be split into.This is a large data payload that needs to be split into.This is a large data payload that needs to be split into."
        payload: str = "105.55|49.59"
        print(f"String length {len(payload)}")
        sender.send(payload=payload)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
