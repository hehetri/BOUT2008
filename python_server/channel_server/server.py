"""Channel server implementation."""
from __future__ import annotations

import logging
import socket
import threading

from .connection import ChannelServerConnection
from .lobby import Lobby
from .sql import SQLDatabase

LOGGER = logging.getLogger(__name__)

PACKETS_HEADER = bytes([0x01, 0x00])
BOT_CREATION_HEADER = bytes([0xE2, 0x2E, 0x02, 0x00])
CREATE_BOT_USERNAME_TAKEN = bytes([0x00, 0x36])
CREATE_BOT_USERNAME_ERROR = bytes([0x00, 0x33])
CREATE_BOT_CREATED = bytes([0x01, 0x00])
CLIENT_NUMBER_HEADER = bytes([0xE0, 0x2E, 0x04, 0x00])
CHARACTER_INFORMATION_HEADER = bytes([0xE1, 0x2E, 0x5E, 0x05])
PLAYERS_HEADER = bytes([0x27, 0x27, 0x13, 0x00])
OK_HEADER = bytes([0x46, 0x2F, 0x20, 0x00])
OK_PACKET = bytes([0x01] + [0x00] * 31)
SERVER_CLIENT_CHECK_1 = bytes([0x01, 0x00, 0x01, 0x00])
SERVER_CLIENT_CHECK_2 = bytes([0xCC])
SERVER_CLIENT_CHECK_ANSWER = bytes([0x02, 0x00, 0x01, 0x00, 0xCC])
NULLBYTE = bytes([0x00])


class ChannelServer(threading.Thread):
    def __init__(self, port: int, sql: SQLDatabase) -> None:
        super().__init__(daemon=True)
        self.port = port
        self.sql = sql
        self._listening = threading.Event()
        self._server_socket: socket.socket | None = None
        self._connections: list[ChannelServerConnection] = []
        self.longnullbyte = NULLBYTE * 1372
        self.lobby = Lobby(NULLBYTE)

    def run(self) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(("0.0.0.0", self.port))
                server.listen()
                self._server_socket = server
                self._listening.set()
                LOGGER.info("ChannelServer (%s) listening", self.port)
                while self._listening.is_set():
                    client_sock, _ = server.accept()
                    connection = ChannelServerConnection(client_sock, self, self.lobby, self.sql)
                    self._connections.append(connection)
                    connection.start()
        except Exception as exc:
            LOGGER.exception("ChannelServer error: %s", exc)

    def stop(self) -> None:
        self._listening.clear()
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                LOGGER.exception("Failed to close channel server socket")

    def remove(self, remote_address: str) -> None:
        self._connections = [c for c in self._connections if c.remote_address != remote_address]
