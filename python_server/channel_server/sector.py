"""Sector map helper."""
from __future__ import annotations


class Sector:
    def __init__(self) -> None:
        self.mapmon = 0

    def get_map_monster(self, map_id: int) -> list[int]:
        if map_id == 0:
            data = [
                2,
                2,
                2,
                2,
                0,
                0,
                0,
                1,
                0,
                0,
                0,
                0,
                2,
                2,
                4,
                4,
                4,
                2,
                82,
                2,
                2,
                2,
                2,
                0,
                0,
                2,
                2,
                1,
                2,
                2,
                0,
                2,
                0,
                0,
                2,
                0,
                3,
                102,
            ]
            self.mapmon = len(data)
            return data
        return []
