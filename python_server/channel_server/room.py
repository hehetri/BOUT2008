"""Room state container (simplified translation)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .bot import BotClass
from .packet import Packet
from .sector import Sector
from .sql import SQLDatabase


@dataclass
class Room:
    roomnum: list[int]
    roomname: str
    roompass: str
    roomlevel: int
    roomowner: str
    roomip: str
    owner_socket: object
    bot: BotClass
    sql: SQLDatabase

    roomtyp: int = -1
    roomstatus: int = 1
    roommap: int = -1
    roomplayer: list[str] = field(default_factory=lambda: [""] * 8)
    roomsocks: list[Optional[object]] = field(default_factory=lambda: [None] * 8)
    roomready: list[bool] = field(default_factory=lambda: [False] * 8)
    roomreadytoplay: list[bool] = field(default_factory=lambda: [False] * 8)
    roomport: list[int] = field(default_factory=lambda: [0] * 8)
    sector: Optional[Sector] = None

    def __post_init__(self) -> None:
        self.roomplayer[0] = self.roomowner
        self.roomsocks[0] = self.owner_socket
        self.roomready[0] = True
        if self.roomnum[0] == 0:
            self.roomtyp = 2
            self.sector = Sector()
        elif self.roomnum[0] == 1:
            self.roomtyp = 0
        elif self.roomnum[0] == 2:
            self.roomtyp = 3

        self.sql.update("INSERT INTO rooms (ip) VALUES (%s)", (self.roomip,))

    def is_empty(self) -> bool:
        return self.roomowner == ""

    def remove_player(self, player: str) -> bool:
        if player not in self.roomplayer:
            return False
        idx = self.roomplayer.index(player)
        self.roomplayer[idx] = ""
        self.roomsocks[idx] = None
        self.roomready[idx] = False
        return all(name == "" for name in self.roomplayer)

    def add_player(self, player: str, sock: object) -> bool:
        for idx, name in enumerate(self.roomplayer):
            if name == "":
                self.roomplayer[idx] = player
                self.roomsocks[idx] = sock
                return True
        return False

    def get_quit_packet(self, slot: int) -> Packet:
        packet = Packet()
        packet.add_header(0x3A, 0x2F)
        packet.add_int(slot, 2, False)
        return packet
