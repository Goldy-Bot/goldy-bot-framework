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
    "command_nuke",
)

logger = LoggerAdapter(app.logger, prefix = Colours.GREEN.apply("command_nuke"))

@app.command()
def command_nuke(
    debug: bool = typer.Option(
        False, help = "Enable extra logging details. THIS WILL SHOW YOUR BOT TOKEN!"
    ),
    cache: bool = typer.Option(
        True, help = "Whether goldy bot should cache or not. If set to false, the cache will be cleared before setup."
    ),
    bot_token: Optional[str] = typer.Option(
        None, help = "Your discord bot token."
    ),
    database_url: Optional[str] = typer.Option(
        None, help = "Your mongoDB database connection url."
    )
):
    """CLI command to delete all registered commands on discord with the goldy bot framework bot in this current working directory."""

    logger.info("Setting up the framework...")

    if debug is True:
        goldy_bot_logger.setLevel(logging.DEBUG)
        app.pretty_exceptions_show_locals = True

    config = Config("./goldy.toml")

    bot_token, database_url = get_token(bot_token, database_url)

    auth = BotAuthentication(bot_token)

    client = HTTPClient()

    shard_manager = ShardManager(
        authentication = auth, 
        intents = GOLDY_INTENTS, 
        http_client = client
    )

    # TODO: Make it where we can run goldy bot completely without a database.
    database = Database(database_url)

    goldy = Goldy(
        http_client = client, 
        shard_manager = shard_manager, 
        database = database, 
        config = config
    )

    if cache is False:
        goldy.clear_cache()

    async def main():
        await goldy.client.setup()

        logger.info("💣 Nuking...")
        await goldy.low_level.create_application_commands([], force = True)

        if config.test_guild_id is not None:
            await goldy.low_level.create_application_commands([], guild_id = config.test_guild_id, force = True)

        logger.info("[Done!]")

        await goldy._clean_up()

    asyncio.run(main())