import click
from click import Context

from . import goldy_bot, goldy_bot_logger

@goldy_bot.group(invoke_without_command=True)
@click.pass_context
def setup(ctx:Context):
    """Creates a goldy bot environment in the directory your currently in for you to run your bot in."""
    if ctx.invoked_subcommand is not None:
        pass
    else:
        normal.invoke(ctx)

@setup.command()
def normal():
    goldy_bot_logger.info("Creating template and environment...")
    ...

@setup.command()
def demo():
    goldy_bot_logger.info("Demo template coming soon...")
    ...