from __future__ import annotations
from typing import Optional

import os
import typer
from cProfile import Profile
from goldy_bot import (
    Goldy, 
    Database, 
    Config, 
    GOLDY_INTENTS
)
from devgoldyutils import LoggerAdapter, Colours

from nextcore.gateway import ShardManager
from nextcore.http import BotAuthentication, HTTPClient

from .__main__ import app, get_token

__all__ = (
    "bench_start_up",
)

logger = LoggerAdapter(app.logger, prefix = Colours.ORANGE.apply("bench_start_up"))

@app.command()
def bench_start_up(
    bot_token: Optional[str] = typer.Option(None, help = "Your discord bot token."),
    database_url: Optional[str] = typer.Option(None, help = "Your mongoDB database connection url.")
):
    bot_token, database_url = get_token(bot_token, database_url)

    with Profile() as profile:
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

    profile.dump_stats("./bench.stats")
    os.system("snakeviz ./bench.stats")