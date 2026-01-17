"""Lobby management for channel server."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional

from .packet import Packet

LOGGER = logging.getLogger(__name__)


@dataclass
class LobbyUser:
    name: str
    bot: int
    writer: Optional[object]
    socket: Optional[object]
    status: int = 1


@dataclass
class Lobby:
    nullbyte: bytes
    max_users: int = 300
    users: List[Optional[LobbyUser]] = field(default_factory=lambda: [None] * 300)
    count: int = 0

    def add_user(self, username: str, bot: int, writer: object, socket: object) -> None:
        for idx in range(self.max_users):
            if self.users[idx] is None:
                self.users[idx] = LobbyUser(username, bot, writer, socket)
                self.count = max(self.count, idx + 1)
                LOGGER.info("User %s added at %s", username, idx)
                self._broadcast(username, self.get_add_packet(username))
                return

    def remove_user(self, username: str) -> None:
        idx = self.get_num(username)
        if idx == -1:
            return
        self._broadcast(username, self.get_del_packet(username))
        self.users[idx] = None
        if idx + 1 == self.count:
            self.count -= 1
        LOGGER.info("User %s removed", username)

    def get_num(self, player: str) -> int:
        for idx in range(self.count):
            user = self.users[idx]
            if user and user.name == player:
                return idx
        return -1

    def get_lobby_packet(self) -> tuple[bytes, bytes]:
        packet = Packet()
        packet.add_header(0xF2, 0x2E)
        packet.add_packet_head(0x01, 0x00)
        packet.add_int(self.count, 2, False)
        for idx in range(self.count):
            user = self.users[idx]
            if not user:
                continue
            name = user.name.encode("latin-1")
            name = name.ljust(15, self.nullbyte)
            packet.add_byte_array(name)
            packet.add_byte2(user.bot & 0xFF, user.status)
        return packet.get_header(), packet.get_packet()

    def get_add_packet(self, username: str) -> tuple[bytes, bytes]:
        idx = self.get_num(username)
        packet = Packet()
        packet.add_header(0x27, 0x27)
        packet.add_packet_head(0x01, 0x00)
        packet.add_string(username)
        packet.add_byte(0x00)
        while packet.get_len() != 17:
            packet.add_byte(0xCC)
        bot = self.users[idx].bot if idx != -1 and self.users[idx] else 0
        status = self.users[idx].status if idx != -1 and self.users[idx] else 0
        packet.add_byte2(bot & 0xFF, status)
        return packet.get_header(), packet.get_packet()

    def get_del_packet(self, username: str) -> tuple[bytes, bytes]:
        idx = self.get_num(username)
        packet = Packet()
        packet.add_header(0x27, 0x27)
        packet.add_packet_head(0x01, 0x00)
        packet.add_string(username)
        packet.add_byte(0x00)
        while packet.get_len() != 17:
            packet.add_byte(0xCC)
        bot = self.users[idx].bot if idx != -1 and self.users[idx] else 0
        packet.add_byte2(bot & 0xFF, 0xFF)
        return packet.get_header(), packet.get_packet()

    def _broadcast(self, username: str, packet: tuple[bytes, bytes]) -> None:
        for idx in range(self.count):
            user = self.users[idx]
            if not user or user.name == username:
                continue
            if user.writer:
                user.writer.write(packet[0])
                user.writer.write(packet[1])
                user.writer.flush()

    def lobby_message(self, msg: str, color: int) -> None:
        packet = Packet()
        packet.add_header(0x1A, 0x27)
        packet.add_byte4(0x00, 0x00, 0x00, 0x00)
        packet.add_int(color, 2, False)
        packet.add_string(f"[Server] {msg}")
        packet.add_byte(0x00)
        head = packet.get_header()
        body = packet.get_packet()
        for idx in range(self.count):
            user = self.users[idx]
            if user and user.writer:
                user.writer.write(head)
                user.writer.write(body)
                user.writer.flush()
