from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Tuple
from decouple import AutoConfig
from devgoldyutils import Colours

from .. import goldy_bot_logger, LoggerAdapter
from ..paths import Paths
from ..errors import GoldyBotError

class NoDiscordToken(GoldyBotError):
    def __init__(self):
        super().__init__(
            "No Discord token was entered! Enter your discord token into the .env file at root or pass it in when initializing Goldy class with the Token class. See '' for more info."
        )

class NoDatabaseToken(GoldyBotError):
    def __init__(self):
        super().__init__(
            "No MongoDB database url was entered! Create and enter a MongoDB database url into the .env file at root or pass it in when initializing Goldy class with the Token class. See '' for more info."
        )

@dataclass
class Token:
    """Handles grabbing the token in many various ways."""
    discord_token:str|None = field(repr=False, default=None)
    database_url:str|None = field(repr=False, default=None)

    def __post_init__(self):
        self.logger = LoggerAdapter(goldy_bot_logger, "Token")

        discord_token, mongodb_url = self.get_token_from_env()

        self.discord_token = (lambda entered_token: discord_token if entered_token is None else entered_token)(self.discord_token)
        self.database_url = (lambda entered_token: mongodb_url if entered_token is None else entered_token)(self.database_url)

        if self.discord_token is None:
            self.create_token_env_file()
            raise NoDiscordToken()

        if self.database_url is None:
            self.create_token_env_file()
            raise NoDatabaseToken()

    def create_token_env_file(self) -> bool:
        if ".env" not in os.listdir("."):
            self.logger.debug("Creating .env file in root dir...")

            # Open template env file.
            template_env_file = open(Paths.TOKEN_ENV_TEMPLATE, mode="r")
            template_env_file.seek(0)

            # Create .env at root.
            env_file = open(".env", mode="w")

            # Copy template to it.
            env_file.write(template_env_file.read())

            self.logger.info(Colours.GREEN.apply_to_string("Created .env file in root dir!"))
            return True

        self.logger.debug("A .env file already exists in root.")
        return False


    def get_token_from_env(self) -> Tuple[str|None, str|None]:
        """
        Returns tuple of tokens from a ``.env`` file.
        
        Tuple index order:

        - ``Discord Bot Token``
        - ``MongoDB Url``
        """
        self.logger.debug("Searching current working directory for .env file if exists...")
        config = AutoConfig(
            search_path=os.getcwd()
        )
        
        # Grabbing tokens.
        # ------------------
        self.logger.debug("Grabbing discord token...")
        discord_token = config(
            "DISCORD_TOKEN", 
            default=None
        )

        self.logger.debug("Grabbing database url...")
        database_token = config(
            "MONGODB_URL", 
            default=None
        )

        # If the placeholder text is still there, set token to None.
        # -----------------------------------------------------------
        if discord_token == "DISCORD BOT TOKEN HERE":
            discord_token = None

        if database_token == "MONGO DATABASE URL HERE":
            database_token = None

        self.logger.debug("Done")

        return discord_token, database_token