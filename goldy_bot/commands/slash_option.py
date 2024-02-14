from __future__ import annotations
from typing import TYPE_CHECKING, Union

from discord_typings import ApplicationCommandOptionData
from discord_typings.interactions.commands import StrCommandOptionChoiceData, IntCommandOptionChoiceData

if TYPE_CHECKING:
    from typing import List, Optional

from enum import Enum
from devgoldyutils import short_str

from GoldyBot import utils

from ..helpers.dict_helper import DictHelper

__all__ = (
    "SlashOptionTypes",
    "SlashOptionChoice",
    "SlashOption"
)

SlashOptionChoiceT = Union[StrCommandOptionChoiceData, IntCommandOptionChoiceData]

class SlashOptionTypes(Enum):
    """An enum class containing some of the slash option types."""
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    ATTACHMENT = 11

class SlashOptionChoice(DictHelper[SlashOptionChoiceT]):
    """A helper class used to create slash option choices."""
    def __init__(self, name: str, value: str | int, **kwargs):
        data: SlashOptionChoiceT = {}

        data["name"] = short_str(name, 99)
        data["value"] = value

        super().__init__(data, **kwargs)

class SlashOption(DictHelper[ApplicationCommandOptionData]):
    r"""
    A class used to create a slash command option.

    ---------------

    ⭐ Example:
    -------------
    This is how you use slash options::

        @GoldyBot.command(slash_options = {
            "bear_name": SlashOption(
                description = "🐻 Pick a bear name.",
                choices = [
                    SlashOptionChoice(name="Simba", value="simba"),
                    SlashOptionChoice(name="Paddington", value="paddington"),
                    SlashOptionChoice(name="Goldilocks", value="goldilocks"),
                    SlashOptionChoice(name="Toto", value="toto")
                ],
                required = True
            )
        })
        async def bear(self, platter: GoldyBot.GoldPlatter, bear_name: str):
            if bear_name == "goldilocks":
                return await platter.send_message("*Goldilocks is not a bear you fool!*", reply=True)

            text = \
                "*> In the woods, there lived three bears in their cozy house. " \
                "There was a small wee bear, a middle-sized bear, " \
                f"and a great, huge bear known as* **{bear_name.title()}**..." \

            await platter.send_message(text, reply=True)

    .. note::

        Try choosing option Goldilocks :)

    .. warning::

        Each SlashOptionChoice MUST have the same value type or else you'll get an invalid form body error from discord :)

    """
    def __init__(
        self, 
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        choices: Optional[List[SlashOptionChoice | str]] = None, 
        type: Optional[SlashOptionTypes] = None, 
        required: bool = True, 
        **kwargs
    ) -> None:
        data: ApplicationCommandOptionData = {}

        if description is None:
            description = "This option has no description. Sorry about that."

        # Check if all choices are same type.
        if choices is not None:
            if isinstance(choices[0], str):
                choices = [SlashOptionChoice(x, x) for x in choices]

            # TODO: Add legibility test for commands.
            #utils.choices_value_check(choices) 

        if type is not None:
            data["type"] = type.value
        else:
            data["type"] = 3


        # If the choices are integer choices set the type of this slash option to 4.
        # This is because type 4 in the discord api means application options with integer choices and type 3 means application options with string choices, FUCK YOU DISCORD!
        # I didn't want to FUCKING have two separate SlashOption classes just for string choices and integer choices FUCK that, so I'm settling with this solution.
        if choices is not None:

            if isinstance(choices[0].data["value"], int):
                data["type"] = 4

            elif isinstance(choices[0].data["value"], bool): # TODO: Try this, idk if this is how it is suppose to work.
                data["type"] = 5


        data["name"] = name # If this is None it will get handled by the Command().params_to_options() function respectively.
        data["description"] = description

        if choices is not None:
            data["choices"] = DictHelper.strip(choices)

        if required:
            data["required"] = True

        super().__init__(data, **kwargs)