from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple

import os
import typer
import asyncio
import logging
from devgoldyutils import Colours
from decouple import AutoConfig

from goldy_bot import (
    Goldy, 
    Database, 
    Config, 
    GOLDY_INTENTS,
    GoldyBotError
)
from goldy_bot.logger import goldy_bot_logger

from nextcore.gateway import ShardManager
from nextcore.http import BotAuthentication, HTTPClient

__all__ = (
    "app",
)

INSTALL_SETUP_LINK = "https://github.com/Goldy-Bot/Goldy-Bot-Framework?tab=readme-ov-file#-installset-up---normal"

app = typer.Typer(pretty_exceptions_show_locals = False)
env_config = AutoConfig(os.getcwd())

@app.command()
def start(
    debug: bool = typer.Option(None, help = "Enable extra logging details. THIS WILL SHOW YOUR BOT TOKEN!"),
    bot_token: Optional[str] = typer.Option(None, help = "Your discord bot token."),
    database_url: Optional[str] = typer.Option(None, help = "Your mongoDB database connection url.")
):
    typer.echo(Colours.ORANGE.apply("Starting..."))

    if debug is not None:
        goldy_bot_logger.setLevel(logging.DEBUG)
        app.pretty_exceptions_show_locals = True

    bot_token, database_url = _get_token(bot_token, database_url)

    auth = BotAuthentication(bot_token)

    client = HTTPClient()

    shard_manager = ShardManager(
        authentication = auth, 
        intents = GOLDY_INTENTS, 
        http_client = client
    )

    database = Database(database_url)
    config = Config("./goldy.toml")

    goldy = Goldy(
        http_client = client, 
        shard_manager = shard_manager, 
        database = database, 
        config = config
    )

    goldy.setup(legacy = True)

    asyncio.run(goldy.start())


def _get_token(bot_token: Optional[str], database_url: Optional[str]) -> Tuple[str, str]:

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