from __future__ import annotations

import sys
import time
import pygame
import asyncio
from datetime import datetime

from nextcore.http.client import HTTPClient

from nextcore.http import BotAuthentication, UnauthorizedError, Route
from nextcore.gateway import ShardManager

from typing import Dict, Any, TYPE_CHECKING, Tuple, Set
from discord_typings import UpdatePresenceData, PartialActivityData, ApplicationData
from devgoldyutils import Colours

from .. import LoggerAdapter, goldy_bot_logger
from ..errors import GoldyBotError
from ..info import VERSION, COPYRIGHT
from ..paths import Paths

from .token import Token

if TYPE_CHECKING:
    from . import objects
    from .objects.invokable import INVOKABLE_TYPES

# Fixes this https://github.com/nextsnake/nextcore/issues/189.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

cache: Dict[str, Any] = {
    "goldy_core_instance": None,
}

class Goldy():
    """The main Goldy Bot class that controls the whole framework and let's you start an instance of Goldy Bot. Also known as the core."""
    def __init__(self, token:Token = None, raise_on_extension_loader_error = None):
        self.token = token
        self.logger = LoggerAdapter(goldy_bot_logger, Colours.ORANGE.apply_to_string("Goldy"))
        self.async_loop = asyncio.get_event_loop()

        # Boot title and copyright stuff.
        print(
            f" {Colours.YELLOW.apply_to_string('Goldy')} {Colours.ORANGE.apply_to_string('Bot')} ({Colours.BLUE.apply_to_string(VERSION)}) - {Colours.PINK_GREY.apply_to_string(COPYRIGHT)}\n"
        )

        # Initializing stuff
        # -------------------
        if self.token is None:
            self.token = Token()
        
        self.nc_authentication = BotAuthentication(self.token.discord_token)
        self.intents = 1 << 9 | 1 << 15

        self.http_client = HTTPClient()
        """Nextcore http client, use this if you would like to perform low level requests."""

        self.shard_manager = ShardManager(
            authentication = self.nc_authentication,
            intents = self.intents,
            http_client = self.http_client,

            presence = UpdatePresenceData(
                activities = [PartialActivityData(name=f"Goldy Bot (v{VERSION})", type=ActivityTypes.PLAYING_GAME.value)],
                since = None,
                status = Status.ONLINE.value,
                afk = False
            )
        )
        """Nextcore shard manager, use if you would like to take control of the shards."""

        self.start_up_time: datetime | None = None
        """The datetime object of when the framework was booted up. Is None if the :py:meth:`~GoldyBot.Goldy.start` method isn't ran."""

        self.pre_invokables: Set[INVOKABLE_TYPES] = set()
        self.invokables: Set[Tuple[str, INVOKABLE_TYPES]] = set()
        """List of all commands, buttons and events registered."""

        self.bot_user: objects.Member = None
        """The bot's user/member object."""
        self.application_data: ApplicationData = None

        # Add to cache.
        cache["goldy_core_instance"] = self

        # Adding shortcuts to sub classes to core class.
        # --------------------------------
        self.database = Database(self)
        """Goldy Bot's class to interface with a Mongo Database asynchronously."""
        self.presence = Presence(self)
        """Class that allows you to control the status, game activity and more of Goldy Bot"""
        self.config = GoldyConfig()
        """
        Class that allows you to retrieve configuration data from the ``goldy.json`` config file. 
        
        All properties return None when not found in the config.
        """
        self.system = System(self)
        """Goldy Bot class used to check how much resources Goldy is utilizing on the host system."""
        self.command_loader = CommandLoader(self)
        """Class that handles command loading."""
        self.command_listener = CommandListener(self)
        """Class that handles the invoking of commands."""
        self.extension_loader = ExtensionLoader(self, raise_on_extension_loader_error)
        """Class that handles extension loading and reloading."""
        self.live_console = LiveConsole(self)
        """The goldy bot live console."""
        self.guild_manager = GuildManager(self)
        self.permission_system = PermissionSystem(self)
        """A goldy bot class that contains methods to handle member/command permissions."""

    @property
    def latency(self) -> float | None:
        """Returns the latency in milliseconds between discord and goldy bot. ``Goldy -> Discord -> Goldy``"""
        try:
            return self.shard_manager.active_shards[0].latency
        except RuntimeError:
            return None
        
    @property
    def up_time(self) -> datetime | None:
        """Returns a datetime object of goldy bot's uptime. Returns None if goldy bot was not started else it will ALWAYS return a datetime object."""
        if self.start_up_time is not None:
            return datetime.fromtimestamp(datetime.now().timestamp() - self.start_up_time.timestamp())
    
        return None

    def start(self):
        """🧡🌆 Awakens Goldy Bot from her hibernation. 😴 Shortcut to ``asyncio.run(goldy.__start_async())`` and also handles various exceptions carefully."""
        try:
            self.async_loop.run_until_complete(
                self.__start_async()
            )
        except KeyboardInterrupt:
            self.stop("Keyboard interrupt detected!")
        #except RuntimeError:
        #    # I really do hope this doesn't torture me in the future. 💀
        #    pass

        return None

    async def __start_async(self):
        self.start_up_time = datetime.now()

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

        await self.pre_setup()
        await self.setup()

        if self.system.in_docker is True: # Live console is disabled when running a docker container.
            self.logger.info(Colours.BLUE.apply("We detected that you are running Goldy Bot in 🐬docker. Live console will be disabled."))
        else:
            self.live_console.start()

        # Raise a error and exit whenever a critical error occurs.
        error = await self.shard_manager.dispatcher.wait_for(lambda reason: True, "critical")

        self.logger.warn(Colours.YELLOW.apply_to_string("Goldy Bot is shutting down..."))
        self.logger.info(Colours.BLUE.apply_to_string(f"Reason: {error[0]}"))

        await self.__stop()

    async def pre_setup(self):
        """Method ran before actual setup. This is used to fetch some data from discord needed by goldy when running the actual setup."""
        r = await self.http_client.request(
            Route(
                "GET", 
                "/oauth2/applications/@me"
            ),
            rate_limit_key = self.nc_authentication.rate_limit_key,
            headers = self.nc_authentication.headers
        )

        self.application_data: ApplicationData = await r.json()
        self.logger.debug("Application data requested!")

        # Get bot's user object.
        # ------------------------
        r = await self.http_client.request(
            Route(
                "GET", 
                "/users/@me"
            ),
            rate_limit_key = self.nc_authentication.rate_limit_key,
            headers = self.nc_authentication.headers
        )

        bot_user = await r.json()
        self.bot_user = Member(bot_user, None, self)
        self.logger.debug("Bot's user object requested!")

    async def setup(self):
        """Method ran to set up goldy bot."""
        await self.guild_manager.setup()
        
        self.extension_loader.load()
        await self.command_loader.load()
        await self.command_listener.start_listening()

    def stop(self, reason: str = "Unknown Reason"):
        """Shuts down goldy bot right away and safely incase anything sussy wussy is going on. 😳"""
        self.live_console.stop()

        # Raises critical error within nextcore and stops it.
        self.async_loop.create_task(
            self.shard_manager.dispatcher.dispatch("critical", "Goldy Exiting: " + reason)
        ) 

    async def stop_async(self, reason:str = "Unknown Reason"):
        """Shuts down goldy bot asynchronously."""
        self.live_console.stop()

        await self.shard_manager.dispatcher.dispatch("critical", "Goldy Exiting: " + reason)

    async def __stop(self):
        """This is an internal method and NOT to be used by you. Use the ``Goldy().stop()`` instead. This method is ran when nextcore raises a critical error."""
        await self.presence.change(Status.INVISIBLE) # Set bot to invisible before shutting off.
        
        self.logger.debug("Closing nextcore http client...")
        await self.http_client.close()

        self.logger.debug("Closing nextcore shard manager...")
        await self.shard_manager.close()

        self.logger.debug("Closing AsyncIOMotorClient...")
        self.database.client.close()
    
        self.logger.debug("Closing async_loop...")
        self.async_loop.stop()

        if self.config.ding_on_exit:
            pygame.mixer.init()
            pygame.mixer.Sound(Paths.ASSETS + "/ding.mp3").play()
            time.sleep(0.5)


# Get goldy instance method.
# ---------------------------
def get_goldy_instance() -> Goldy | None:
    """Returns instance of goldy core class."""
    return cache["goldy_core_instance"]

get_core = get_goldy_instance
"""Returns instance of goldy core class."""
get_goldy = get_goldy_instance
"""Returns instance of goldy core class."""


# Root imports.
# -------------
from .system import System
from .database import Database
from .presence import Presence, Status, ActivityTypes
from .goldy_config import GoldyConfig
from .extensions.extension_loader import ExtensionLoader
from .commands.loader import CommandLoader
from .commands.listener import CommandListener
from .live_console import LiveConsole
from .objects import Member
from .guilds import GuildManager
from .permission_system import PermissionSystem