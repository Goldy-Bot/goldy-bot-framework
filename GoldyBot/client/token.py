from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Tuple
from decouple import config, AutoConfig
from devgoldyutils import Colours

from .. import goldy_bot_logger, LoggerAdapter
from ..paths import Paths
from ..errors import GoldyBotError

class NoDiscordToken(GoldyBotError):
    def __init__(self):
        if not ".env" in os.listdir("."):
            goldy_bot_logger.debug("Creating .env file in root dir...")

            # Open template env file.
            template_env_file = open(Paths.TOKEN_ENV, mode="r")
            template_env_file.seek(0)

            # Create .env at root.
            env_file = open(".env", mode="w")
            
            # Copy template to it.
            env_file.write(template_env_file.read())

            goldy_bot_logger.info(Colours.GREEN.apply_to_string("Created .env file in root dir!"))

        super().__init__(
            "No Discord token was entered! Enter your discord token into the .env file at root or pass it in when initializing Goldy class with the Token class. See '' for more info."
        )

@dataclass
class Token:
    """Handles grabbing the token in many various ways."""
    discord_token:str|None = field(repr=False, default=None)
    database_token:str|None = field(repr=False, default=None)

    def __post_init__(self):
        self.logger = LoggerAdapter(goldy_bot_logger, "Token")

        discord_token, mongodb_token = self.get_token_from_env()

        self.discord_token = (lambda entered_token: discord_token if entered_token is None else entered_token)(self.discord_token)
        self.database_token = (lambda entered_token: mongodb_token if entered_token is None else entered_token)(self.database_token)

        if self.discord_token is None:
            raise NoDiscordToken()


    def get_token_from_env(self) -> Tuple[str|None, str|None]:
        """
        Returns tuple of tokens from a ``.env`` file.
        
        Tuple index order:

        - ``Discord Bot Token``
        - ``MongoDB Token``
        """
        self.logger.debug("Searching current working directory for .env file if exists...")
        config = AutoConfig(
            search_path=os.getcwd()
        )
        
        # Grabbing tokens.
        # ------------------
        self.logger.debug("Grabbing discord token...")
        discord_token = config(
            "TOKEN", 
            default=None
        )

        self.logger.debug("Grabbing database token...")
        database_token = config(
            "MONGODB_TOKEN", 
            default=None
        )

        # If the placeholder text is still there, set token to None.
        # -----------------------------------------------------------
        if discord_token == "DISCORD BOT TOKEN HERE":
            discord_token = None

        if database_token == "MONGO DATABASE TOKEN HERE":
            database_token = None

        self.logger.debug("Done")

        return discord_token, database_token