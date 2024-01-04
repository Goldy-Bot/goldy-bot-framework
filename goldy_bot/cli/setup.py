from __future__ import annotations

import typer
import shutil
import goldy_bot
from pathlib import Path
from devgoldyutils import LoggerAdapter, Colours

from .__main__ import app

__all__ = (
    "setup",
)

DOT_ENV_CONTENTS = '# DISCORD_TOKEN=\n# MONGODB_URL="mongodb://localhost:27017"'

logger = LoggerAdapter(app.logger, prefix = Colours.ORANGE.apply("setup"))

@app.command()
def setup(
    path: str = typer.Option(".", help = "The path goldy bot should drop it's template files in."),
):
    """Generates goldy.toml config and some other useful files."""
    destination_path = Path(path)

    if not destination_path.exists():
        logger.info("That directory doesn't exist so I'm creating it...")
        destination_path.mkdir()

    goldy_toml = destination_path.joinpath("goldy.toml")

    if not goldy_toml.exists():
        logger.info("Generating goldy.toml file...")

        goldy_toml_template = Path(goldy_bot.__file__).parent.joinpath("goldy.template.toml")
        shutil.copy(goldy_toml_template, goldy_toml)

    extensions_folder = destination_path.joinpath("extensions")

    if not extensions_folder.exists():
        logger.info("Creating extensions directory...")
        extensions_folder.mkdir()

    dot_env = destination_path.joinpath(".env")

    if not dot_env.exists():
        logger.info("Creating .env file...")

        with dot_env.open("w") as file:
            file.write(DOT_ENV_CONTENTS)

    logger.info("All good! :)")