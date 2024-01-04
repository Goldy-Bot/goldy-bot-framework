from __future__ import annotations
from typing import Optional

import typer
import logging
import asyncio
from devgoldyutils import LoggerAdapter, Colours

from goldy_bot import (
    Goldy, 
    Database, 
    Config, 
    GOLDY_INTENTS
)
from goldy_bot.logger import goldy_bot_logger

from nextcore.gateway import ShardManager
from nextcore.http import BotAuthentication, HTTPClient

from .__main__ import app, get_token

__all__ = (
    "start",
)

logger = LoggerAdapter(app.logger, prefix = Colours.ORANGE.apply("start"))

@app.command()
def start(
    debug: bool = typer.Option(None, help = "Enable extra logging details. THIS WILL SHOW YOUR BOT TOKEN!"),
    bot_token: Optional[str] = typer.Option(None, help = "Your discord bot token."),
    database_url: Optional[str] = typer.Option(None, help = "Your mongoDB database connection url.")
):
    """Convenient cli command to start up the goldy bot framework in this current working directory."""
    logger.info(Colours.ORANGE.apply("Awakening her..."))

    if debug is not None:
        goldy_bot_logger.setLevel(logging.DEBUG)
        app.pretty_exceptions_show_locals = True

    bot_token, database_url = get_token(bot_token, database_url)

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