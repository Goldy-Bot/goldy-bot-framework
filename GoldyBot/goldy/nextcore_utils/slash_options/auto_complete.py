from __future__ import annotations
from typing import List, TYPE_CHECKING, overload, Callable, Union
from discord_typings import ApplicationCommandOptionData, AutocompleteInteractionData

from nextcore.http import Route
from devgoldyutils import LoggerAdapter, Colours

from .... import goldy_bot_logger
from .slash_option import SlashOption, SlashOptionChoice
from ...objects.member import Member
from ...objects.platter.golden_platter import GoldPlatter

if TYPE_CHECKING:
    from .... import Goldy
    from ...commands.slash_command import SlashCommand
    from ...extensions import Extension

    AUTO_COMPLETE_CALLBACK = Callable[[Extension, str], List[SlashOptionChoice | str]]

class SlashOptionAutoComplete(SlashOption):
    @overload
    def __init__(
        self, 
        callback: AUTO_COMPLETE_CALLBACK, 
        name: str = None, 
        description: str = None, 
        required: bool = True, 
        **extra: ApplicationCommandOptionData
    ) -> None:
        ...

    @overload
    def __init__(
        self, 
        recommendations: List[SlashOptionChoice | str], 
        name: str = None, 
        description: str = None, 
        required: bool = True, 
        **extra: ApplicationCommandOptionData
    ) -> None:
        ...

    def __init__(
        self, 
        name: str = None, 
        description: str = None, 
        callback: AUTO_COMPLETE_CALLBACK = None, 
        recommendations: List[SlashOptionChoice | str] = None, 
        required: bool = True, 
        **extra: ApplicationCommandOptionData
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
            # TODO: Where I left off last night (15/07/2023)

        else: # If no callback was given then default to recommendations list.
            for choice in self.recommendations: # Some shit fuzzy searching. I'll improve it later :L
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