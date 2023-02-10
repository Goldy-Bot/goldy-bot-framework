from __future__ import annotations

import sys
import asyncio

from nextcore.http.client import HTTPClient

from nextcore.http import BotAuthentication, UnauthorizedError
from nextcore.gateway import ShardManager

from typing import cast, Dict, Any
from discord_typings import UpdatePresenceData
from devgoldyutils import Colours

from .. import LoggerAdapter, goldy_bot_logger
from ..errors import GoldyBotError

from .token import Token

# Fixes this https://github.com/nextsnake/nextcore/issues/189.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

cache:Dict[str, Any] = {
    "goldy_core_instance": None,
}

class Goldy():
    """The main Goldy Bot class that controls the whole framework and let's you start an instance of Goldy Bot. Also known as the core."""
    def __init__(self, token:Token = None):
        self.token = None
        self.logger = LoggerAdapter(goldy_bot_logger, Colours.ORANGE.apply_to_string("Goldy"))
        self.async_loop = asyncio.get_event_loop()

        # Initializing stuff
        # -------------------
        if token is None:
            self.token = Token()
        else:
            self.token = token
        
        self.nc_authentication = BotAuthentication(self.token.discord_token)
        self.intents = 1 << 9 | 1 << 15

        self.http_client = HTTPClient()

        self.shard_manager = ShardManager(
            authentication = self.nc_authentication,
            intents = self.intents,
            http_client = self.http_client,

            presence = UpdatePresenceData(
                activities=[],
                since=None,
                status=Status.ONLINE.value,
                afk=False
            )
        )

        # Add to cache.
        cache["goldy_core_instance"] = self

        # Adding shortcuts to sub classes to core class.
        # --------------------------------
        self.presence = Presence(self)

    def start(self):
        """🧡🌆 Awakens Goldy Bot from her hibernation. 😴 Shortcut to ``asyncio.run(goldy.__start_async())`` and also handles various exceptions carefully."""
        try:
            self.async_loop.run_until_complete(
                self.__start_async()
            )
        except KeyboardInterrupt:
            self.stop("Keyboard interrupt detected!")

        return None

    async def __start_async(self):
        await self.http_client.setup()

        # This should return once all shards have started to connect.
        # This does not mean they are connected.
        try:
            await self.shard_manager.connect()
            self.logger.debug("Nextcore shard manager connecting...")
        except UnauthorizedError as e:
            raise GoldyBotError(
                f"Nextcord shard manager failed to connect! We got '{e.message}' from nextcord. This might mean your discord token is incorrect!"
            )

        # Log when shards are ready.
        self.shard_manager.event_dispatcher.add_listener(
            lambda x: self.logger.info(f"Nextcore shards are {Colours.GREEN.apply_to_string('connected')} and {Colours.BLUE.apply_to_string('READY!')}"), 
            event_name="READY"
        )

        # TODO: Run Goldy Bot setup method here.

        # Raise a error and exit whenever a critical error occurs
        error = await self.shard_manager.dispatcher.wait_for(lambda: True, "critical")

        raise cast(Exception, error)

    def stop(self, reason:str = "Unknown Reason"):
        """Shuts down goldy bot right away and safely incase anything sussy wussy is going on. 😳"""
        self.logger.warn(Colours.YELLOW.apply_to_string("Goldy Bot is shutting down..."))
        self.logger.info(Colours.BLUE.apply_to_string(f"Reason: {reason}"))
        
        self.async_loop.run_until_complete(self.http_client.close())
        self.async_loop.run_until_complete(self.shard_manager.close())

        self.async_loop.stop()

        return None


# Root imports.
# -------------
from .presence import Presence, Status


# Get goldy instance method.
# ---------------------------
def get_goldy_instance() -> Goldy | None:
    """Returns instance of goldy core class."""
    return cache["goldy_core_instance"]

get_core = get_goldy_instance
get_goldy = get_goldy_instance