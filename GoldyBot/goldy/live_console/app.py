from __future__ import annotations

import cmd2
from typing import TYPE_CHECKING, Tuple

from ... import log, utils
from ..extensions import extensions_cache, Extension

if TYPE_CHECKING:
    from ... import Goldy

class LiveConsoleApp(cmd2.Cmd):
    def __init__(self, goldy: Goldy, logger: log.Logger) -> None:
        self.goldy = goldy
        self.logger = logger
        super().__init__()

    def do_reload(self, extension_name: cmd2.Statement):
        # Reload goldy.json...
        # ---------------------
        self.goldy.config.__init__()

        # Reload extensions...
        # ----------------------
        extension = None
        if not extension_name == "":
            extension: Tuple[str, Extension] | None = utils.cache_lookup(extension_name, extensions_cache, False)

            if extension is None:
                self.logger.error(f"The extension '{extension_name}' was not found.")
                return False
            else:
                self.logger.info(f"Found '{extension[1].name}'.")

        self.logger.info("Reloading extension(s)...")
        self.logger.warning("This may take a minute to begin...")
        self.goldy.async_loop.create_task(
            self.goldy.extension_loader.reload(
                (lambda x: [x[1]] if x is not None else None)(extension)
            )
        )

        # Rerun guilds setup...
        # ----------------------
        self.goldy.guild_manager.guilds.clear()

        self.goldy.async_loop.create_task(
            self.goldy.guild_manager.setup()
        )

    def do_reload_configs(self, _: cmd2.Statement):
        self.goldy.config.__init__()

        self.goldy.guild_manager.guilds.clear()

        self.logger.warning("Wait, we're reloading guilds... (This may halt the bot for a while!)")
        self.goldy.async_loop.create_task(
            self.goldy.guild_manager.setup()
        )

    def do_quit(self, _: cmd2.Statement):
        self.logger.info("Exiting...")
        self.goldy.stop("Console master commanded me to stop!")

    def do_exit(self, _: cmd2.Statement):
        self.onecmd("quit")

    def do_stop(self, _: cmd2.Statement):
        self.onecmd("quit")