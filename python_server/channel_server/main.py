"""Entry point for the channel server."""
from __future__ import annotations

import logging

from .gui import ChannelGameServerGUI
from .server import ChannelServer
from .sql import SQLDatabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    sql = SQLDatabase("ChannelServer")
    sql.start()

    server = ChannelServer(11002, sql)
    server.start()
    gui = ChannelGameServerGUI()
    gui.write("ChannelServer started")
    server.join()


if __name__ == "__main__":
    main()
