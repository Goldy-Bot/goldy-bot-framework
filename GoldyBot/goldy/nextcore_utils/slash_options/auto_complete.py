from __future__ import annotations

from typing import List, TYPE_CHECKING
from discord_typings import ApplicationCommandOptionData, AutocompleteInteractionData

from nextcore.http import Route
from devgoldyutils import LoggerAdapter, Colours

from .... import goldy_bot_logger
from .slash_option import SlashOption, SlashOptionChoice
from ...objects.member import Member

if TYPE_CHECKING:
    from .... import Goldy
    from ...commands.slash_command import SlashCommand

class SlashOptionAutoComplete(SlashOption):
    def __init__(
        self, 
        recommendations: List[SlashOptionChoice | str], 
        name: str = None, 
        description: str = None, 
        required: bool = True, 
        **extra: ApplicationCommandOptionData
    ) -> None:

        if isinstance(recommendations[0], str):
            recommendations = [SlashOptionChoice(x, x) for x in recommendations]

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

        member = Member(data["member"]["user"], goldy.guild_manager.get_guild(data["guild_id"]), goldy)
        self.logger.debug(f"We got --> '{current_typing_value}' from {member.name}#{member.discriminator}")

        # Implemented some fuzzy searching.
        for choice in self.recommendations:
            if current_typing_value.lower() in choice["name"].lower():
                payload["choices"].append(choice)

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