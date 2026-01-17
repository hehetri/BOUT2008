"""Channel server connection handler."""
from __future__ import annotations

import logging
import socket
import threading
from typing import Optional

from . import server as server_module
from .lobby import Lobby
from .misc import compare_chat, getcmd
from .packet import Packet
from .sql import SQLDatabase

LOGGER = logging.getLogger(__name__)


class ChannelServerConnection(threading.Thread):
    def __init__(self, sock: socket.socket, server: server_module.ChannelServer, lobby: Lobby, sql: SQLDatabase) -> None:
        super().__init__(daemon=True)
        self.sock = sock
        self.server = server
        self.lobby = lobby
        self.sql = sql
        self.account: Optional[str] = None
        self.remote_address = sock.getpeername()[0]
        self.writer = sock.makefile("wb")

    def run(self) -> None:
        try:
            self._check_account()
            if not self.account or self.account == "a":
                LOGGER.warning("Connection rejected for %s", self.remote_address)
                return

            self.lobby.add_user(self.account, 0, self.writer, self.sock)

            while True:
                packet = self._read_packet()
                if packet is None:
                    break
                header, payload = packet
                cmd = int.from_bytes(header[:2], "big")
                self._parse_cmd(cmd, header + payload)
        except Exception as exc:
            LOGGER.exception("Channel connection error: %s", exc)
        finally:
            if self.account:
                self.lobby.remove_user(self.account)
            try:
                self.writer.close()
                self.sock.close()
            except Exception:
                LOGGER.exception("Error closing connection")

    def _read_packet(self) -> Optional[tuple[bytes, bytes]]:
        header = self._recv_exact(4)
        if not header:
            return None
        length = int.from_bytes(header[2:4], "little")
        payload = self._recv_exact(length)
        if payload is None:
            return None
        return header, payload

    def _recv_exact(self, length: int) -> Optional[bytes]:
        data = bytearray()
        while len(data) < length:
            chunk = self.sock.recv(length - len(data))
            if not chunk:
                return None
            data.extend(chunk)
        return bytes(data)

    def _check_account(self) -> None:
        try:
            rows = self.sql.query(
                "SELECT username, banned FROM bout_users WHERE current_ip=%s LIMIT 1",
                (self.remote_address,),
            )
            if rows:
                if int(rows[0].get("banned", 0)) == 0:
                    self.account = rows[0].get("username")
        except Exception as exc:
            LOGGER.exception("Error checking account: %s", exc)
        if not self.account:
            self.account = "a"

    def _parse_cmd(self, cmd: int, packet: bytes) -> None:
        LOGGER.debug("Parse cmd %s", hex(cmd))
        if cmd == 0xF82A:
            self._send_raw(server_module.CLIENT_NUMBER_HEADER + b"\x01\x00\x01\x00")
            return
        if cmd == 0xF92A:
            self._send_character_info()
            return
        if cmd == 0x1A27:
            self._handle_chat(packet)
            return
        if cmd == 0x742B:
            self._send_ok()
            return
        self._send_ok()

    def _send_character_info(self) -> None:
        payload = b"\x00\x35" + self.server.longnullbyte
        self._send_raw(server_module.CHARACTER_INFORMATION_HEADER + payload)

    def _handle_chat(self, packet: bytes) -> None:
        pack = Packet()
        pack.set_packet(packet)
        pack.remove_header()
        message = pack.get_string(0, pack.get_len(), False)
        if self.account and compare_chat(message.encode("latin-1"), self.account, False, False) != -1:
            self.lobby.lobby_message(message, 0)
        else:
            LOGGER.warning("Chat name mismatch from %s", self.account)

    def _send_ok(self) -> None:
        self._send_raw(server_module.OK_HEADER + server_module.OK_PACKET)

    def _send_raw(self, payload: bytes) -> None:
        self.writer.write(payload)
        self.writer.flush()
