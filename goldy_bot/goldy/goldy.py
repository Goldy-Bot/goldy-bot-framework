from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, TypedDict, Dict

    from nextcore.http import HTTPClient
    from nextcore.gateway import ShardManager

    from ..config import Config
    from ..database import Database

    KeyAndHeadersT = TypedDict("KeyAndHeaders", {"rate_limit_key": str, "headers": Dict[str, str]})

from pathlib import Path
from datetime import datetime
from devgoldyutils import LoggerAdapter, Colours
from nextcore.http import UnauthorizedError

from .wrappers import FrameworkWrapper, LowLevelWrapper

from .. import errors
from ..commands import CommandType
from ..logger import goldy_bot_logger

__all__ = (
    "Goldy",
)

class Goldy(
    FrameworkWrapper
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
        self.client: HTTPClient = http_client
        self.shard_manager: ShardManager = shard_manager

        self.database = database
        """An instance of the framework's mongo database."""
        self.config = config

        self.boot_datetime: Optional[datetime] = None
        """The time and date the framework spun up."""

        self.key_and_headers: KeyAndHeadersT = {
            "rate_limit_key": self.shard_manager.authentication.rate_limit_key, 
            "headers": self.shard_manager.authentication.headers
        }
        """Shorthand attribute you can use to pass rate limit keys and headers to ``nextcore.http.HTTPClient.request()``."""

        self.logger = LoggerAdapter(goldy_bot_logger, Colours.ORANGE.apply("Goldy"))
        self.low_level = LowLevelWrapper(self)
        """
        WARNING: Misuse of these methods WILL result in breakage of the framework. Only use them if you know what you are doing!
        """

        super().__init__()

    async def start(self) -> None:
        """Starts Goldy Bot 🥞 Pancake."""
        self.boot_datetime = datetime.now()

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
            lambda _: self.logger.info(
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

    async def setup(self, legacy: bool = False, database_check: bool = True) -> None:
        """
        Does the setup for you if you would not like to handle it yourself. 
        Pulling extensions, loading extensions, registering commands and etc.
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
            extension_metadata = self._get_extension_metadata(path)

            if extension_metadata is None:
                self.logger.warn(
                    f"Couldn't grab metadata from pyproject.toml for the extension at '{path}' " \
                        "as it does not have a pyproject.toml file. Dependency installer will cease to function " \
                            "causing missing dependencies."
                )

            else:
                self._install_missing_extension_deps(
                    extension_metadata, self.config.extensions_raise_on_load_error
                )

            extension = self._load_extension(path, legacy = legacy)

            if extension is not None:
                self.logger.info(f"The extension '{extension.name}' has been loaded!")

                if not self.is_extension_ignored(extension):
                    self.add_extension(extension)

                else:
                    self.logger.warning(
                        f"The extension '{extension.name}' is not being added as it's ignored!"
                    )

        # Load goldy bot internal extensions.
        internal_extensions_dir = Path(__file__).parent.parent.joinpath("internal_extensions")

        for path in internal_extensions_dir.iterdir():
            extension = self._load_extension(path, legacy = legacy)

            if extension is not None:
                self.logger.info(f"Internal extension '{extension.name}' has been loaded!")

                self.add_extension(extension)

        # Setting up nextcore client.
        await self.client.setup()

        # Registering commands.
        await self._sync_commands()

        # Check if database is ok.
        if database_check:
            is_okay, msg = await self.database._is_connection_ok()

            if is_okay:
                self.logger.info("AsyncIOMotorClient (Database) " + Colours.GREEN.apply_to_string("Is Okay!"))
            else:
                self.logger.critical(msg)

        # Set command listener.
        self.shard_manager.event_dispatcher.add_listener(
            lambda x: self.invoke_command(
                x["data"].get("name", x["data"].get("custom_id")), CommandType(x["type"]), x
            ),
            event_name = "INTERACTION_CREATE"
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
        await self.client.close()
        await self.shard_manager.close()