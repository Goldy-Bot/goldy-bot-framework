from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple
    from click import Context

__all__ = ("add", "pull")

import os
import json
import click
from .. import Goldy

from . import goldy_bot, goldy_bot_logger

@goldy_bot.command()
@click.argument("extensions", nargs=-1)
@click.pass_context
def add(ctx: Context, extensions: Tuple[str]):
    """Adds a goldy bot extension."""
    if len(extensions) == 0:
        goldy_bot_logger.error(f"You must include an extension! \n{add.get_usage(ctx)}")
        return False

    if "goldy.json" not in os.listdir():
        goldy_bot_logger.error(
            "We can't find your 'goldy.json' file. Please make sure you are in the same directory or that you have created a goldy bot environment with 'goldybot setup'."
        )
        return False

    goldy_bot_logger.info("Adding the extension(s)...")

    goldy_json_file = open("./goldy.json", mode = "r+", encoding = "utf+8")
    goldy_config = json.load(goldy_json_file)

    for extension in extensions:

        if extension not in goldy_config["goldy"]["extensions"]["include"]:
            goldy_config["goldy"]["extensions"]["include"].append(extension)
        else:
            goldy_bot_logger.warning(f"'{extension}' is already included.")

    goldy_json_file.seek(0)
    json.dump(goldy_config, goldy_json_file, indent = 4, ensure_ascii = False)
    goldy_json_file.close()

    goldy_bot_logger.info("Edited config.")

@goldy_bot.command()
def pull():
    """Pulls the extensions from GitHub."""
    goldy = Goldy(display_copyright = False)
    goldy.extension_loader.pull()

    goldy_bot_logger.info("Extensions pulled!")