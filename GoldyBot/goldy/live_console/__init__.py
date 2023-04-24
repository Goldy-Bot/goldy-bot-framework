from __future__ import annotations

import cmd2
import time
import threading
import _thread
from typing import TYPE_CHECKING
from devgoldyutils import Colours
from ... import goldy_bot_logger, LoggerAdapter

if TYPE_CHECKING:
    from .. import Goldy

class LiveConsole(threading.Thread):
    """The goldy bot live console."""
    def __init__(self, goldy:Goldy) -> None:
        """The goldy bot live console."""
        self.goldy = goldy
        self.logger = LoggerAdapter(goldy_bot_logger, prefix = Colours.PURPLE.apply_to_string("LiveConsole"))

        self.__stop = False
        super().__init__(daemon = True)

    def run(self) -> None:
        time.sleep(1)

        app = LiveConsoleApp(self.goldy, self.logger)

        app.preloop()

        while self.__stop is False:
            print("")
            try:
                app.onecmd(input("> "))
            except cmd2.exceptions.EmptyStatement:
                pass

    def stop(self):
        self.__stop = True

from .app import LiveConsoleApp