import os
import click
from click import Context
from devgoldyutils import Colours

from . import goldy_bot, goldy_bot_logger
from ..paths import Paths
from ..file_templates import FileTemplates
from ..goldy.token import Token

@goldy_bot.group(invoke_without_command=True)
@click.pass_context
def setup(ctx:Context):
    """Creates a goldy bot environment in the directory your currently in for you to run your bot from."""
    goldy_bot_logger.info("Creating template and environment...")

    if ctx.invoked_subcommand is not None:
        pass
    else:
        normal.invoke(ctx)

@setup.command()
def normal():
    # TODO: Place code that generates environment here.

    file_templates = FileTemplates([
        Paths.GOLDY_JSON,
        Paths.RUN_SCRIPT,
        Paths.TOKEN_ENV
    ])

    file_templates.copy_to(".")

    try:
        os.rename("token.env", ".env")
    except FileExistsError:
        goldy_bot_logger.debug("'.env' already exists so I'm going to delete the one I was about to copy into root.")
        os.remove("token.env")
    

@setup.command()
def demo():
    goldy_bot_logger.info("Demo template coming soon...")
    ...