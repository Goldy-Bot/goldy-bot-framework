from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple

import os
import typer
from decouple import AutoConfig
from devgoldyutils import Colours, LoggerAdapter

from goldy_bot import GoldyBotError
from goldy_bot.logger import goldy_bot_logger

__all__ = (
    "app",
)

INSTALL_SETUP_LINK = "https://github.com/Goldy-Bot/Goldy-Bot-Framework?tab=readme-ov-file#-installset-up---normal"

app = typer.Typer(pretty_exceptions_show_locals = False)
app.logger = LoggerAdapter(goldy_bot_logger, prefix = "cli")

env_config = AutoConfig(os.getcwd())

def get_token(bot_token: Optional[str], database_url: Optional[str]) -> Tuple[str, str]:

    if bot_token is None:
        bot_token = env_config("DISCORD_TOKEN", None)

    if database_url is None:
        database_url = env_config("MONGODB_URL", None)

    if bot_token is None or database_url is None:
        raise GoldyBotError(
            "Either the discord bot token or mongoDB url is missing.\n"
            "Please enter them in their respective environment variables: DISCORD_TOKEN, MONGODB_URL\n" \
            f"{Colours.RESET}Learn more at {INSTALL_SETUP_LINK}"
        )

    return bot_token, database_url