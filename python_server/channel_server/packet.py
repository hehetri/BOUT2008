"""Packet construction/parsing helpers."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Packet:
    packet: bytearray = bytearray()
    header: bytearray = bytearray()
    header_calced: bool = False

    def add_header(self, b1: int, b2: int) -> None:
        self.header = bytearray([b1 & 0xFF, b2 & 0xFF])
        self.header_calced = False

    def remove_header(self) -> None:
        del self.packet[:4]

    def _calc_header(self) -> None:
        length = len(self.packet)
        self.header.extend(length.to_bytes(2, "little"))
        self.header_calced = True

    def get_header(self) -> bytes:
        if not self.header_calced:
            self._calc_header()
        return bytes(self.header)

    def add_packet_head(self, b1: int, b2: int) -> None:
        self.packet.extend([b1 & 0xFF, b2 & 0xFF])

    def add_string(self, string: str) -> None:
        self.packet.extend(string.encode("latin-1"))

    def add_int(self, value: int, num: int, reverse: bool) -> None:
        data = value.to_bytes(num, "little")
        if reverse:
            data = data[::-1]
        self.packet.extend(data)

    def add_byte(self, b1: int) -> None:
        self.packet.append(b1 & 0xFF)

    def add_byte2(self, b1: int, b2: int) -> None:
        self.packet.extend([b1 & 0xFF, b2 & 0xFF])

    def add_byte4(self, b1: int, b2: int, b3: int, b4: int) -> None:
        self.packet.extend([b1 & 0xFF, b2 & 0xFF, b3 & 0xFF, b4 & 0xFF])

    def add_byte_array(self, data: bytes) -> None:
        self.packet.extend(data)

    def get_packet(self) -> bytes:
        return bytes(self.packet)

    def get_len(self) -> int:
        return len(self.packet)

    def set_packet(self, data: bytes) -> None:
        self.packet = bytearray(data)

    def get_int(self, bytec: int) -> int:
        chunk = bytes(self.packet[:bytec])
        del self.packet[:bytec]
        return int.from_bytes(chunk[::-1], "big")

    def get_string(self, start: int, end: int, nulled: bool) -> str:
        chunk = bytes(self.packet[start:end])
        del self.packet[:end]
        if nulled:
            return chunk.decode("latin-1")
        return chunk.split(b"\x00", 1)[0].decode("latin-1")

    def clean(self) -> None:
        self.packet = bytearray()
        self.header = bytearray()
        self.header_calced = False
