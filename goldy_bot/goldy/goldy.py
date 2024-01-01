from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

    from nextcore.http import HTTPClient
    from nextcore.gateway import ShardManager

    from ..database import Database
    from ..config import Config

from datetime import datetime
from devgoldyutils import LoggerAdapter, Colours
from nextcore.http import UnauthorizedError

from .. import errors
from .wrappers import LegacyWrapper, ExtensionsWrapper
from ..logger import goldy_bot_logger

__all__ = (
    "Goldy",
)

class Goldy(LegacyWrapper, ExtensionsWrapper):
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

        super().__init__(self)

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

        # TODO: Add these to the main framework classes.
        # await self.pre_setup() 
        await self._legacy_setup()

        # Raise a error and exit whenever a critical error occurs.
        error = await self.shard_manager.dispatcher.wait_for(lambda reason: True, "critical")

        self.logger.info(Colours.BLUE.apply_to_string(
            f"Nextcore gateway has closed for the reason '{error[0]}'.")
        )

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