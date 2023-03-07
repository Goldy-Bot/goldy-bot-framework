from __future__ import annotations

import cmd2
from typing import TYPE_CHECKING, Tuple

from .. import utils
from ... import log
from ..extensions import extensions_cache, Extension

if TYPE_CHECKING:
    from ... import Goldy

class LiveConsoleApp(cmd2.Cmd):
    def __init__(self, goldy:Goldy, logger:log.Logger) -> None:
        self.goldy = goldy
        self.logger = logger
        super().__init__()

    def do_reload(self, extension_name: cmd2.Statement):
        extension = None
        if not extension_name == "":
            extension:Tuple[str, Extension] | None = utils.cache_lookup(extension_name, extensions_cache)

            if extension is None:
                self.logger.error(f"The extension '{extension_name}' was not found.")
                return False
        
        self.logger.info(f"Reloading extension(s)...")
        self.goldy.async_loop.create_task(self.goldy.extension_reloader.reload((lambda x: x[1] if x is not None else None)(extension)))

    def do_quit(self, _: cmd2.Statement):
        self.logger.debug("Exiting...")
        self.goldy.stop("Console master commanded me to stop!")

    def do_exit(self, _: cmd2.Statement):
        self.onecmd("quit")

    def do_stop(self, _: cmd2.Statement):
        self.onecmd("quit")