"""Entry point for the login server."""
from __future__ import annotations

import logging

from .room_udp_server import RoomUDPServer
from .server import LoginServer
from .sql import SQLDatabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    sql = SQLDatabase("LoginServer")
    sql.start()

    login_server = LoginServer(11000, sql)
    login_server.start()

    udp_server = RoomUDPServer(sql)
    udp_server.start()

    login_server.join()


if __name__ == "__main__":
    main()
