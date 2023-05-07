"""
Theses are errors that report back to the front end. 
For example if a command is missing a parameter it will raise a FrontEndError which will report back the command user.
"""
import logging as log

from ... import errors
from .colours import Colours
from .embeds.embed import Embed
from ..objects.golden_platter import GoldPlatter, PlatterType

class FrontEndErrors(errors.GoldyBotError):
    def __init__(
            self, 
            title: str,
            description: str,
            message: str,
            platter: GoldPlatter, 
            embed_colour = Colours.AKI_ORANGE,
            delete_after = 6,
            logger: log.Logger = None
        ):

        platter.goldy.async_loop.create_task(
            platter.send_message(
                embeds = [
                    Embed(
                        title = title,
                        description = description,
                        colour = embed_colour
                    )
                ],
                reply = True,
                delete_after = (lambda: None if platter.type.value == PlatterType.SLASH_CMD.value else delete_after)(),
                flags = (lambda: 1 << 6 if platter.type.value == PlatterType.SLASH_CMD.value else None)()
            )
        )

        super().__init__(message, logger)


class MissingArgument(FrontEndErrors):
    def __init__(self, missing_args: list, platter: GoldPlatter, logger: log.Logger = None):
        missing_args_string = ""
        for arg in missing_args:
            missing_args_string += f"{arg}, "

        super().__init__(
            title = "🧡 Oops, your missing an argument.", 
            description = f"""
            *You missed the argument(s): ``{missing_args_string[:-2]}``*

            **Command Usage -> ``{platter.guild.prefix}{platter.command.command_usage}``**
            """, # TODO: Add command usage string to command class.
            message = f"The command author missed the arguments -> '{missing_args_string[:-2]}'.",
            platter = platter, 
            logger = logger
        )


class TooManyArguments(FrontEndErrors):
    def __init__(self, platter: GoldPlatter, logger: log.Logger = None):
        super().__init__(
            title = ":heart: You gave me too many arguments.", 
            description = f"""
            This command doesn't take that many arguments or it doesn't take any arguments at all.

            **Command Usage -> ``{platter.guild.prefix}{platter.command.command_usage}``**
            """, 
            message = "The command author passed too many arguments.",
            platter = platter, 
            embed_colour = Colours.RED,
            logger = logger
        )


class MissingPerms(FrontEndErrors):
    def __init__(self, platter: GoldPlatter, logger: log.Logger = None):
        super().__init__(
            title = ":heart: No Perms!", 
            description = "Sorry, you don't have the perms to run this command.",
            message = f"The command author '{platter.author.username}#{platter.author.discriminator}' doesn't have the perms to run this command.",
            platter = platter, 
            embed_colour = Colours.RED,
            logger = logger
        )


class OnlyAuthorCanInvokeRecipe(FrontEndErrors):
    def __init__(self, platter: GoldPlatter, logger: log.Logger = None):
        super().__init__(
            title = "🧡 Only Author Can Invoke", 
            description = "Sorry, only the command author can invoke this.",
            message = f"'{platter.author.username}#{platter.author.discriminator}' tried to invoke an 'author only' recipe.",
            platter = platter, 
            embed_colour = Colours.AKI_ORANGE,
            logger = logger
        )