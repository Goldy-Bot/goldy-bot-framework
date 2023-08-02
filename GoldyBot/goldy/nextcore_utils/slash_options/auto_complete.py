from __future__ import annotations
from typing import List, TYPE_CHECKING, overload, Callable, Union
from discord_typings import AutocompleteOptionData, AutocompleteInteractionData

from nextcore.http import Route
from devgoldyutils import LoggerAdapter, Colours

from .... import goldy_bot_logger
from .slash_option import SlashOption, SlashOptionChoice
from ...objects.member import Member

if TYPE_CHECKING:
    from .... import Goldy
    from ...commands.slash_command import SlashCommand
    from ...extensions import Extension

    AUTO_COMPLETE_CALLBACK = Callable[[Extension, str], List[Union[SlashOptionChoice, str]]]

class SlashOptionAutoComplete(SlashOption):
    r"""
    Like :py:meth:`~GoldyBot.SlashOption` but it auto completes while the member is typing and it doesn't force them to pick those options.
    You can also override the callback and implement your own auto complete mechanism like I did in mal_cord (https://github.com/THEGOLDENPRO/mal_cord/blob/main/__init__.py#L23).

    ---------------

    ⭐ Example:
    -------------
    This is how you use auto complete slash options::

        @GoldyBot.command(
            slash_options = {
                "bear_name": SlashOptionAutoComplete( # Now when you type these choices will be recommended to you but not forced on you.
                    description = "⭐ Pick a custom bear name.",
                    recommendations = [
                        "Simba",
                        "Paddington",
                        "Goldilocks",
                        "Toto"
                    ]
                )
            }
        )
        async def custom_bear(self, platter: GoldyBot.GoldPlatter, bear_name: str):
            if bear_name.lower() == "goldilocks":
                return await platter.send_message("*Goldilocks is not a bear you fool!*", reply=True)

            text = \
                "*> In the woods, there lived three bears in their cozy house. " \
                "There was a small wee bear, a middle-sized bear, " \
                f"and a great, huge bear known as* **{bear_name}**..." \

            await platter.send_message(text, reply=True)

    .. note::

        More at https://goldybot.devgoldy.xyz/examples.slash_options.html

    """
    @overload
    def __init__(
        self, 
        callback: AUTO_COMPLETE_CALLBACK, 
        name: str = None, 
        description: str = None, 
        required: bool = True, 
        **extra: AutocompleteOptionData
    ) -> None:
        ...

    @overload
    def __init__(
        self, 
        recommendations: List[SlashOptionChoice | str], 
        name: str = None, 
        description: str = None, 
        required: bool = True, 
        **extra: AutocompleteOptionData
    ) -> None:
        ...

    def __init__(
        self, 
        name: str = None, 
        description: str = None, 
        callback: AUTO_COMPLETE_CALLBACK = None, 
        recommendations: List[SlashOptionChoice | str] = None, 
        required: bool = True, 
        **extra: AutocompleteOptionData
    ) -> None:

        if recommendations is None:
            recommendations = []

        self.callback = callback
        self.recommendations = recommendations

        self.logger = LoggerAdapter(goldy_bot_logger, prefix=Colours.PURPLE.apply("SlashOptionAutoComplete"))

        super().__init__(
            name = name, 
            description = description, 
            required = required, 

            autocomplete = True,
            **extra
        )

    async def send_auto_complete(
        self,
        data: AutocompleteInteractionData,
        current_typing_value: str,
        command: SlashCommand,
        goldy: Goldy, 
    ) -> None:

        payload = {}
        payload["choices"] = []

        choices: List[SlashOptionChoice | str] = []

        member = Member(data["member"]["user"], goldy.guild_manager.get_guild(data["guild_id"]), goldy)

        self.logger.debug(f"We got --> '{current_typing_value}' from {member}")

        if self.callback is not None:
            choices = await self.callback(command.extension, current_typing_value) # Might add a platter for this in the future, idk yet.

        else: # If no callback was given then default to recommendations list.
            for choice in self.recommendations: # Some shit fuzzy searching. I'll improve it later :L
                if isinstance(choice, str):
                    choice = SlashOptionChoice(choice, choice)

                if current_typing_value.lower() in choice["name"].lower():
                    choices.append(choice)

        choices = [SlashOptionChoice(x, x) if isinstance(x, str) else x for x in choices]
        payload["choices"] = choices[:24] # Discord only allows max of 25 choices.

        self.logger.debug(
            f"Sending auto complete '{payload['choices']}' to --> slash command '{command.name}'."
        )

        await goldy.http_client.request(
            Route(
                "POST", 
                "/interactions/{interaction_id}/{interaction_token}/callback", 
                interaction_id = data["id"], 
                interaction_token = data["token"]
            ),
            rate_limit_key = goldy.nc_authentication.rate_limit_key,
            json = {
                "type": 8, 
                "data": payload
            }
        )

        return None