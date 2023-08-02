"""
Theses are errors that report back to the front end. 
For example if a command is missing a parameter it will raise a FrontEndError which will report back the command user.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import logging as log

from ... import errors
from .colours import Colours
from .embeds.embed import Embed

if TYPE_CHECKING:
    from .. import objects

class FrontEndErrors(errors.GoldyBotError):
    def __init__(
            self, 
            embed: Embed,
            message: str,
            platter: objects.GoldPlatter, 
            delete_after = 8,
            logger: log.Logger = None
        ):
        from  ..commands import slash_command

        platter.goldy.async_loop.create_task(
            platter.send_message(
                embeds = [
                    embed
                ],
                reply = True, 
                delete_after = None if isinstance(platter.invokable, slash_command.SlashCommand) else delete_after,
                flags = 1 << 6 if isinstance(platter.invokable, slash_command.SlashCommand) else None
            )
        )

        super().__init__(message, logger)


class MissingArgument(FrontEndErrors):
    def __init__(self, missing_args: list, platter: objects.GoldPlatter, logger: log.Logger = None):
        missing_args_string = ""
        for arg in missing_args:
            missing_args_string += f"{arg}, "

        super().__init__(
            embed = Embed(
                title = "🧡 Oops, you're missing an argument.", 
                description = f"""
                *You missed the argument(s): ``{missing_args_string[:-2]}``*

                ```
                Command Usage -> {platter.guild.config_wrapper.prefix}{platter.invokable.command_usage}
                ```
                """,
                colour = Colours.AKI_ORANGE
            ),
            message = f"The command author missed the arguments -> '{missing_args_string[:-2]}'.",
            platter = platter, 
            delete_after = 10,
            logger = logger
        )


class InvalidArguments(FrontEndErrors):
    def __init__(self, platter: objects.GoldPlatter, logger: log.Logger = None):
        super().__init__(
            embed = Embed(
                title = "⚠️ Invalid Arguments!", 
                description = f"""
                The arguments you entered for this command are invalid.

                One of these could be the cause:
                - This command takes a sub command and you mistyped it.
                - This command doesn't take that many arguments.
                - It doesn't take any arguments at all.

                ```
                Command Usage -> {platter.guild.config_wrapper.prefix}{platter.invokable.command_usage}
                ```
                """,
                colour = Colours.YELLOW
            ),
            message = "The command author passed too many arguments.",
            platter = platter, 
            delete_after = 30,
            logger = logger
        )


class MissingPerms(FrontEndErrors):
    def __init__(self, platter: objects.GoldPlatter, logger: log.Logger = None):
        # Don't raise front end error if the command is hidden and is a prefix command.
        # This insures prefix commands are truly hidden.
        # The git issue: https://github.com/Goldy-Bot/Goldy-Bot-V5/issues/54
        from  ..commands import prefix_command

        message = f"The command author '{platter.author.username}#{platter.author.discriminator}' doesn't have the perms to run this command."

        if platter.invokable.hidden and isinstance(platter.invokable, prefix_command.PrefixCommand):
            raise errors.GoldyBotError(message)

        super().__init__(
            embed = Embed(
                title = ":heart: No Perms!", 
                description = "Sorry, you don't have the perms to run this command.",
                colour = Colours.RED
            ),
            message = message,
            platter = platter, 
            logger = logger
        )


class CommandIsDisabled(FrontEndErrors):
    def __init__(self, platter: objects.GoldPlatter, logger: log.Logger = None):
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
    def __init__(self, platter: objects.GoldPlatter, logger: log.Logger = None):
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
    def __init__(self, platter: objects.GoldPlatter, logger: log.Logger = None):
        super().__init__(
            embed = Embed(
                title = "🧡 Only Author Can Invoke", 
                description = "Sorry, only the command author can invoke this.",
                colour = Colours.AKI_ORANGE
            ),
            message = f"'{platter.author}' tried to invoke an 'author only' recipe.",
            platter = platter, 
            logger = logger
        )

class UnknownError(FrontEndErrors):
    def __init__(self, platter: objects.GoldPlatter, error: Exception = None, logger: log.Logger = None):
        # If the exception caught is a goldy bot exception continue raising that exception otherwise raise this unknown exception.
        if error is not None and isinstance(error, errors.GoldyBotError):
            raise error

        super().__init__(
            embed = Embed(
                title = "❤️ An Error Occurred!", 
                description = "Oopsie daisy, an internal unknown error occurred. *Sorry I'm still new to this.* 🥺",
                colour = Colours.RED,
                footer = {
                    "text": "Report button will be coming soon."
                }
            ),
            message = f"Error occurred in the command '{platter.invokable.name}' executed by '{platter.author}'!",
            platter = platter, 
            delete_after = 12,
            logger = logger
        )