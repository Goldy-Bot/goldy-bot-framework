from __future__ import annotations

from typing import List
from discord_typings import ApplicationCommandOptionData

from GoldyBot.goldy.nextcore_utils.slash_options.slash_option import SlashOptionChoice, SlashOptionTypes

from .slash_option import SlashOption

class SlashOptionAutoComplete(SlashOption):
    def __init__(
        self, 
        recommendations: List[SlashOptionChoice | str], 
        name: str = None, 
        description: str = None, 
        required: bool = True, 
        **extra: ApplicationCommandOptionData
    ) -> None:

        if isinstance(recommendations, str):
            recommendations = [SlashOptionChoice(x, x) for x in recommendations]

        self.recommendations = recommendations

        super().__init__(
            name = name, 
            description = description, 
            required = required, 

            autocomplete = True,
            **extra
        )