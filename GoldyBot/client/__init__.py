from __future__ import annotations

import sys
import asyncio

from nextcore.http.client import HTTPClient

from nextcore.http import BotAuthentication, UnauthorizedError
from nextcore.gateway import ShardManager

from typing import cast
from discord_typings import MessageData, UpdatePresenceData, ChannelData
from devgoldyutils import Colours

from .. import LoggerAdapter, goldy_bot_logger
from ..errors import GoldyBotError

from .token import Token
from .presence import Status

# Fixes this https://github.com/nextsnake/nextcore/issues/189.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Goldy():
    """The main Goldy Bot client class that controls the whole framework and let's you start an instance of Goldy Bot."""
    def __init__(self, token:Token = None):
        self.token = None
        self.logger = LoggerAdapter(goldy_bot_logger, Colours.ORANGE.apply_to_string("Goldy"))
        self.async_loop = asyncio.get_event_loop()

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


    async def change_presence(self, status:Status=None, afk:bool=None) -> bool|None:
        """Allows you to update the presence of Goldy Bot. Like e.g ``online, idle, dnd``."""
        if status is None and afk is None:
            return None

        self.logger.debug("Changing Goldy Bot presence...")

        for shard in self.shard_manager.active_shards:
            presence = shard.presence
            new_presence = presence

            if not status is None:
                if isinstance(status, Status):
                    presence["status"] = status.value
                else:
                    presence["status"] = status
            
            if not afk is None:
                presence["afk"] = afk

            await shard.presence_update(presence)
            self.logger.debug(f"Updated presence for shard {shard.shard_id} from '{presence}' to '{new_presence}'!")

        self.logger.info("Goldy Bot presence changed successfully!")
        return True


    def start(self):
        """🧡🌆 Awakens Goldy Bot from her hibernation. 😴 Shortcut to ``asyncio.run(goldy.__start_async())`` and also handles various exceptions carefully."""
        try:
            self.async_loop.run_until_complete(
                self.__start_async()
            )
        except KeyboardInterrupt:
            self.async_loop.run_until_complete(
                self.stop("Keyboard interrupt detected!")
            )

            self.async_loop.close()

    async def __start_async(self):
        await self.http_client.setup()

        # This should return once all shards have started to connect.
        # This does not mean they are connected.
        try:
            await self.shard_manager.connect()
        except UnauthorizedError as e:
            raise GoldyBotError(
                f"Nextcord shard manager failed to connect! We got '{e.message}' from nextcord. This might mean your discord token is incorrect!"
            )

        # Raise a error and exit whenever a critical error occurs
        error = await self.shard_manager.dispatcher.wait_for(lambda: True, "critical")

        raise cast(Exception, error)

    async def stop(self, reason:str = "Unknown Reason"):
        """Shuts down goldy bot right away incase anything sussy wussy is going on. 😳"""
        self.logger.warn(Colours.YELLOW.apply_to_string("Goldy Bot is shutting down..."))
        self.logger.info(Colours.BLUE.apply_to_string(f"Reason: {reason}"))
        
        await self.http_client.close()
        await self.shard_manager.close()
        sys.exit(0)