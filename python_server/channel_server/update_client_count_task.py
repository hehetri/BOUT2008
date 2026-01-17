"""Update client count task placeholder."""
from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)


class UpdateClientCountTask:
    def __init__(self, server, gui) -> None:
        self.server = server
        self.gui = gui

    def run(self) -> None:
        count = self.server.get_client_count()
        msg = f"{count} client" + ("s" if count != 1 else "")
        if self.gui:
            self.gui.set_client_count(msg)
        LOGGER.info("Client count updated: %s", msg)
