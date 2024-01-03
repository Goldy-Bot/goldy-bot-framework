from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

    from nextcore.http import HTTPClient
    from nextcore.gateway import ShardManager

    from ..config import Config
    from ..database import Database

from pathlib import Path
from datetime import datetime
from devgoldyutils import LoggerAdapter, Colours
from nextcore.http import UnauthorizedError

from .. import errors
from .wrappers import (
    LegacyWrapper, 
    DockerWrapper, 
    ExtensionsWrapper,
    RepoWrapper
)
from ..logger import goldy_bot_logger

__all__ = (
    "Goldy",
)

class Goldy(
    LegacyWrapper, 
    DockerWrapper, 
    ExtensionsWrapper,
    RepoWrapper
):
    """
    The core class that wraps nextcore's shard manager and client. The framework's core class.
    """
    def __init__(
        self, 
        http_client: HTTPClient,
        shard_manager: ShardManager,
        database: Database,
        config: Config
    ) -> None:
        self.http_client = http_client
        self.shard_manager = shard_manager

        self.database = database
        """An instance of the framework's mongo database."""
        self.config = config

        self.boot_datetime: Optional[datetime] = None
        """The time and date the framework spun up."""

        self.logger = LoggerAdapter(goldy_bot_logger, Colours.ORANGE.apply("Goldy"))

        super().__init__()

    async def start(self) -> None:
        """Starts Goldy Bot 🥞 Pancake."""
        self.boot_datetime = datetime.now()

        await self.http_client.setup()

        try:
            await self.shard_manager.connect()
            self.logger.debug("Nextcore shard manager connecting...")

        except UnauthorizedError as e:
            raise errors.GoldyBotError(
                f"""
                Nextcore's shard manager failed to connect! We got '{e.message}' from nextcore. 
                This may mean your discord token is incorrect!
                """,
                logger = self.logger
            )

        # Log when shards are ready.
        self.shard_manager.event_dispatcher.add_listener(
            lambda x: self.logger.info(
                f"Nextcore shards are {Colours.GREEN.apply('connected')} and {Colours.BLUE.apply('READY!')}"
            ), 
            event_name = "READY"
        )

        await self._legacy_setup()

        # Raise a error and exit whenever a critical error occurs.
        error = await self.shard_manager.dispatcher.wait_for(lambda reason: True, "critical")

        self.logger.info(Colours.BLUE.apply_to_string(
            f"Nextcore gateway has closed for the reason '{error[0]}'.")
        )

    def setup(self, legacy: bool = False) -> None:
        """
        Does the setup for you if you would not like to handle it yourself. 
        Pulling extensions, loading extensions, loading commands and etc.
        """
        self.logger.info("Running goldy bot setup...")

        if legacy is True:
            self._initialize_legacy_goldy()

        extensions_dir = Path(self.config.extensions_directory)
        included_extensions = self.config.included_extensions

        # Removing unwanted extensions.
        self._remove_unwanted_extensions(
            extensions_dir, included_extensions
        )

        # Getting git ready.
        self.logger.info("Setting up git...")
        self._git_setup()

        # Pull included extensions with git.
        self.logger.info("Pulling extensions...")
        for extension in included_extensions:
            self.pull_extension(extension, extensions_dir)

        # Loading extensions.
        self.logger.info("Loading extensions...")
        for path in extensions_dir.iterdir():
            extension = self.load_extension(path, legacy = legacy)

            if extension is not None:
                self.logger.info(f"The extension '{extension.name}' has been loaded!")

                self.add_extension(extension)

    async def stop(self, reason: Optional[str] = None) -> None:
        """Stops Goldy Bot Pancake."""
        reason = reason or "goldy.stop() was executed. (No reason was given)"

        await self.shard_manager.dispatcher.dispatch(
            "critical", reason
        )

        await self._clean_up()

    async def _clean_up(self) -> None:
        """Cleans up the framework by closing clients and more."""
        await self.http_client.close()
        await self.shard_manager.close()