"""Login server implementation."""
from __future__ import annotations

import logging
import socket
import threading

from .connection import LoginServerConnection
from .sql import SQLDatabase

LOGGER = logging.getLogger(__name__)


class LoginServer(threading.Thread):
    def __init__(self, port: int, sql: SQLDatabase) -> None:
        super().__init__(daemon=True)
        self.port = port
        self.sql = sql
        self._listening = threading.Event()
        self._server_socket: socket.socket | None = None
        self._connections: list[LoginServerConnection] = []

    def run(self) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(("0.0.0.0", self.port))
                server.listen()
                self._server_socket = server
                self._listening.set()
                LOGGER.info("LoginServer (%s) started and listening", self.port)
                while self._listening.is_set():
                    client_sock, _ = server.accept()
                    connection = LoginServerConnection(client_sock, self.sql)
                    self._connections.append(connection)
                    connection.start()
        except Exception as exc:
            LOGGER.exception("LoginServer error: %s", exc)

    def stop(self) -> None:
        self._listening.clear()
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                LOGGER.exception("Failed to close server socket")

    def get_client_count(self) -> int:
        return len(self._connections)
