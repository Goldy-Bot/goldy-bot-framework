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
            embed: Embed,
            message: str,
            platter: GoldPlatter, 
            delete_after = 8,
            logger: log.Logger = None
        ):

        platter.goldy.async_loop.create_task(
            platter.send_message(
                embeds = [
                    embed
                ],
                reply = True,
                delete_after = None if platter.type.value == PlatterType.SLASH_CMD.value else delete_after,
                flags = 1 << 6 if platter.type.value == PlatterType.SLASH_CMD.value else None
            )
        )

        super().__init__(message, logger)


class MissingArgument(FrontEndErrors):
    def __init__(self, missing_args: list, platter: GoldPlatter, logger: log.Logger = None):
        missing_args_string = ""
        for arg in missing_args:
            missing_args_string += f"{arg}, "

        super().__init__(
            embed = Embed(
                title = "🧡 Oops, you're missing an argument.", 
                description = f"""
                *You missed the argument(s): ``{missing_args_string[:-2]}``*

                **Command Usage -> ``{platter.guild.prefix}{platter.command.command_usage}``**
                """, # TODO: Add command usage string to command class.
                colour = Colours.AKI_ORANGE
            ),
            message = f"The command author missed the arguments -> '{missing_args_string[:-2]}'.",
            platter = platter, 
            delete_after = 10,
            logger = logger
        )


class TooManyArguments(FrontEndErrors):
    def __init__(self, platter: GoldPlatter, logger: log.Logger = None):
        super().__init__(
            embed = Embed(
                title = ":heart: You gave me too many arguments.", 
                description = f"""
                This command doesn't take that many arguments or it doesn't take any arguments at all.

                **Command Usage -> ``{platter.guild.prefix}{platter.command.command_usage}``**
                """,
                colour = Colours.RED
            ),
            message = "The command author passed too many arguments.",
            platter = platter, 
            delete_after = 10,
            logger = logger
        )


class MissingPerms(FrontEndErrors):
    def __init__(self, platter: GoldPlatter, logger: log.Logger = None):
        super().__init__(
            embed = Embed(
                title = ":heart: No Perms!", 
                description = "Sorry, you don't have the perms to run this command.",
                colour = Colours.RED
            ),
            message = f"The command author '{platter.author.username}#{platter.author.discriminator}' doesn't have the perms to run this command.",
            platter = platter, 
            logger = logger
        )


class CommandIsDisabled(FrontEndErrors):
    def __init__(self, platter: GoldPlatter, logger: log.Logger = None):
        super().__init__(
            embed = Embed(
                title = "❤️ This command is disabled!", 
                description = "Sorry, the extension this command belongs to is currently disabled.",
                colour = Colours.RED
            ),
            message = "The command's extension is disabled.",
            platter = platter, 
            logger = logger
        )


class ExtensionNotAllowedInGuild(FrontEndErrors):
    def __init__(self, platter: GoldPlatter, logger: log.Logger = None):
        super().__init__(
            embed = Embed(
                title = "🧡 Not Enabled In Guild!", 
                description = "Sorry, the extension this command belongs to is not currently enabled in this guild (server).",
                colour = Colours.AKI_ORANGE
            ),
            message = f"The command's extension is not allowed in the guild '{platter.guild.code_name}', check the guild's config on the database.",
            platter = platter, 
            logger = logger
        )


class OnlyAuthorCanInvokeRecipe(FrontEndErrors):
    def __init__(self, platter: GoldPlatter, logger: log.Logger = None):
        super().__init__(
            embed = Embed(
                title = "🧡 Only Author Can Invoke", 
                description = "Sorry, only the command author can invoke this.",
                colour = Colours.AKI_ORANGE
            ),
            message = f"'{platter.author.username}#{platter.author.discriminator}' tried to invoke an 'author only' recipe.",
            platter = platter, 
            logger = logger
        )