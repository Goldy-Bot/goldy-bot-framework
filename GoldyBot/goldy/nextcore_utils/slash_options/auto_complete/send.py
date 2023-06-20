from __future__ import annotations

from typing import TYPE_CHECKING
from discord_typings import ApplicationCommandOptionInteractionData, AutocompleteInteractionData

from nextcore.http import Route

if TYPE_CHECKING:
    from .... import Goldy, commands

async def send_auto_complete(
    data: AutocompleteInteractionData,
    goldy: Goldy, 
    current_typing_option: ApplicationCommandOptionInteractionData, 
    command: commands.Command
) -> None:
    
    payload = {}

    print("<<<", command.slash_options)
    for option in command.slash_options:
        option = command.slash_options[option]

        print(">", option["name"], current_typing_option["name"])

        if option["name"] == current_typing_option["name"]:
            payload["choices"] = option["choices"]
            break

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

    print(">>", payload)

    return None