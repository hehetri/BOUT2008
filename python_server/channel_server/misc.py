"""Misc helper functions matching the legacy Java behavior."""
from __future__ import annotations


def bytetoint(data: bytes) -> int:
    hex_data = "".join(f"{byte:02x}" for byte in data[::-1])
    return int(hex_data, 16) if hex_data else 0


def getbyte(value: int, num: int) -> bytes:
    return value.to_bytes(num, "little")


def getcmd(packet: bytes) -> int:
    hex_data = "".join(f"{byte:02x}" for byte in packet[:2])
    return int(hex_data, 16) if hex_data else 0


def compare_chat(chatpack: bytes, rlcharname: str, whisper: bool, isgm: bool) -> int:
    if not whisper:
        if (len(chatpack) > 6 and chatpack[4] != 0x00) or (len(chatpack) > 6 and chatpack[6] != 0x5B and not isgm):
            return -1
    try:
        a = chatpack.index(0x5B)
        b = chatpack.index(0x5D, a)
    except ValueError:
        return -1
    if b - a > 16:
        return -1
    chname = chatpack[a + 1 : b].decode("latin-1")
    return a if chname == rlcharname else -1


def remove_nullbyte(data: bytes) -> str:
    return data.split(b"\x00", 1)[0].decode("latin-1")
