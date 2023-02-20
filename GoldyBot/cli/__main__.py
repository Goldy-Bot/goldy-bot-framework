import click
from devgoldyutils import Colours
from .. import VERSION, goldy_bot_logger

G = Colours.YELLOW.apply_to_string
O = Colours.ORANGE.apply_to_string

@click.group(invoke_without_command=True)
@click.pass_context
def goldy_bot(ctx:click.Context):

    if ctx.invoked_subcommand is None:

        # Splash title from https://patorjk.com/software/taag/#p=display&f=Big%20Money-ne&t=Goldy%20Bot
        print(G("  /$$$$$$            /$$       /$$") + O("                 /$$$$$$$              /$$    "))
        print(G(" /$$__  $$          | $$      | $$") + O("                | $$__  $$            | $$    "))
        print(G("| $$  \__/  /$$$$$$ | $$  /$$$$$$$ /$$   /$$") + O("      | $$  \ $$  /$$$$$$  /$$$$$$  "))
        print(G("| $$ /$$$$ /$$__  $$| $$ /$$__  $$| $$  | $$") + O("      | $$$$$$$  /$$__  $$|_  $$_/  "))
        print(G("| $$|_  $$| $$  \ $$| $$| $$  | $$| $$  | $$") + O("      | $$__  $$| $$  \ $$  | $$    "))
        print(G("| $$  \ $$| $$  | $$| $$| $$  | $$| $$  | $$") + O("      | $$  \ $$| $$  | $$  | $$ /$$"))
        print(G("|  $$$$$$/|  $$$$$$/| $$|  $$$$$$$|  $$$$$$$") + O("      | $$$$$$$/|  $$$$$$/  |  $$$$/"))
        print(G(" \______/  \______/ |__/ \_______/ \____  $$") + O("      |_______/  \______/    \___/  "))
        print(G("                                   /$$  | $$"))
        print(G("                                  |  $$$$$$/"))
        print(G("                                   \______/"))
        print(f"    {O('Version: [')} {G(VERSION)} {O(']')}")
        print("")

        print(
            Colours.BLUE.apply_to_string("Do 'goldybot --help' for a list of available commands.")
        )

    else:

        goldy_bot_logger.info(
            Colours.ORANGE.apply_to_string(
                f"Running the command --> [{ctx.invoked_subcommand}]..."
            )
        )
        print("")