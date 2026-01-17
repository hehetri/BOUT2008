"""Console-based GUI replacement."""
from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)


class ChannelGameServerGUI:
    def __init__(self) -> None:
        self.client_count = "0 clients"

    def write(self, msg: str) -> None:
        LOGGER.info(msg)

    def set_client_count(self, msg: str) -> None:
        self.client_count = msg
        LOGGER.info("Client count: %s", msg)
