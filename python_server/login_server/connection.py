"""Login server connection handler."""
from __future__ import annotations

import hashlib
import logging
import socket
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .sql import SQLDatabase

LOGGER = logging.getLogger(__name__)

LOGIN_SUCCESSBYTE = bytes(
    [
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x01,
        0xFF,
        0x00,
    ]
    + [0x00] * 68
)
LOGIN_INCUSERBYTE = bytes(
    [
        0x01,
        0x00,
        0x02,
        0x00,
        0x00,
        0x00,
        0xFF,
        0x00,
    ]
    + [0x00] * 68
)
LOGIN_INCPASSBYTE = bytes(
    [
        0x01,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0xFF,
        0x00,
    ]
    + [0x00] * 68
)
LOGIN_BANUSERBYTE = bytes(
    [
        0x01,
        0x00,
        0x03,
        0x00,
        0x00,
        0x00,
        0xFF,
        0x00,
    ]
    + [0x00] * 68
)
LOGIN_ALREADYLOGGEDIN = bytes(
    [
        0x01,
        0x00,
        0x06,
        0x00,
        0x00,
        0x00,
        0xFF,
        0x00,
    ]
    + [0x00] * 68
)
LOGINHEADER = bytes([0xEC, 0x2C, 0x4A, 0x00])


@dataclass
class LoginResult:
    code: int
    message: str


class LoginServerConnection(threading.Thread):
    def __init__(self, sock: socket.socket, sql: SQLDatabase) -> None:
        super().__init__(daemon=True)
        self.sock = sock
        self.sql = sql
        self.user: Optional[str] = None
        self.password_hash: Optional[str] = None

    def run(self) -> None:
        try:
            with self.sock:
                while True:
                    data = self._read_null_terminated()
                    if data is None:
                        break
                    if data.startswith("H"):
                        self.user = data[1:]
                        LOGGER.info("[CLIENT-Username] %s", self.user)
                    elif len(data) == 32:
                        self.password_hash = data
                        LOGGER.info("[CLIENT-Password-Hash] %s", self.password_hash)
                        self._do_login()
                        break
        except Exception as exc:
            LOGGER.exception("Login connection error: %s", exc)

    def _read_null_terminated(self) -> Optional[str]:
        buffer = bytearray()
        while len(buffer) < 300:
            chunk = self.sock.recv(1)
            if not chunk:
                return None
            if chunk == b"\x00":
                return buffer.decode("latin-1")
            buffer.extend(chunk)
        return buffer.decode("latin-1")

    def _do_login(self) -> None:
        result = self._check_user()
        if result.code == 0:
            self._update_account(self.user or "")
            self._send(LOGINHEADER + LOGIN_SUCCESSBYTE)
        elif result.code == 1:
            self._send(LOGINHEADER + LOGIN_INCUSERBYTE)
        elif result.code == 2:
            self._send(LOGINHEADER + LOGIN_INCPASSBYTE)
        elif result.code == 3:
            self._send(LOGINHEADER + LOGIN_BANUSERBYTE)
        elif result.code == 4:
            self._send(LOGINHEADER + LOGIN_ALREADYLOGGEDIN)
        LOGGER.info("[SERVER] Login Sent (%s)", result.message)

    def _check_user(self) -> LoginResult:
        if not self.user or not self.password_hash:
            return LoginResult(1, "Incorrect Username")
        try:
            rows = self.sql.query(
                "SELECT id, username, password, banned, online FROM bout_users WHERE username=%s LIMIT 1",
                (self.user,),
            )
        except Exception as exc:
            LOGGER.exception("Error querying user: %s", exc)
            return LoginResult(1, "Incorrect Username")

        if not rows:
            return LoginResult(1, "Incorrect Username")

        record = rows[0]
        stored_hash = self._md5_hash(record.get("password", ""))
        banned = int(record.get("banned", 0))
        online = int(record.get("online", 0))
        if stored_hash != self.password_hash:
            return LoginResult(2, "Incorrect Password")
        if banned == 1:
            return LoginResult(3, "Banned Username")
        if online == 1:
            return LoginResult(4, "User is already Logged in")
        return LoginResult(0, "Success")

    def _update_account(self, user: str) -> None:
        try:
            rows = self.sql.query(
                "SELECT logincount FROM bout_users WHERE username=%s LIMIT 1",
                (user,),
            )
            count = int(rows[0]["logincount"]) if rows else 0
            count += 1
            ip = self.sock.getpeername()[0]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.sql.update(
                "UPDATE bout_users SET current_ip=%s, logincount=%s, last_ip=%s, lastlogin=%s WHERE username=%s",
                (ip, count, ip, timestamp, user),
            )
        except Exception as exc:
            LOGGER.exception("Error updating account: %s", exc)

    @staticmethod
    def _md5_hash(text: str) -> str:
        return hashlib.md5(text.encode("latin-1")).hexdigest()

    def _send(self, payload: bytes) -> None:
        self.sock.sendall(payload)
