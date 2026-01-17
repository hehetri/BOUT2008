"""UDP room server to update room ports."""
from __future__ import annotations

import logging
import socket
import threading

from .sql import SQLDatabase

LOGGER = logging.getLogger(__name__)


class RoomUDPServer(threading.Thread):
    def __init__(self, sql: SQLDatabase, port: int = 11011) -> None:
        super().__init__(daemon=True)
        self.sql = sql
        self.port = port

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("0.0.0.0", self.port))
            while True:
                data, addr = sock.recvfrom(1024)
                if data.startswith(b"\xC9\x00"):
                    ip = addr[0]
                    port = addr[1]
                    LOGGER.info("UDP save port %s of IP %s", port, ip)
                    try:
                        self.sql.update(
                            "UPDATE rooms SET port=%s WHERE ip=%s AND port=0",
                            (port, ip),
                        )
                    except Exception:
                        LOGGER.exception("Failed updating room port")
