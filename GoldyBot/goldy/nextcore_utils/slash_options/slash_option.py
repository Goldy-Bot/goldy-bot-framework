from __future__ import annotations

from typing import List
from discord_typings import ApplicationCommandOptionData
from discord_typings.interactions.commands import StrCommandOptionChoiceData, IntCommandOptionChoiceData

from GoldyBot.errors import GoldyBotError

class SlashOptionChoice(dict):
    """A class used to create slash option choice."""
    def __init__(self, name:str, value: str|int, **extra):
        """
        Creates an slash option choice. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-option-choice-structure
        """
        data: StrCommandOptionChoiceData | IntCommandOptionChoiceData = {}

        data["name"] = name
        data["value"] = value

        data.update(extra)

        super().__init__(data)
        

class SlashOption(dict):
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
        async def bear(self, platter: GoldyBot.GoldenPlatter, bear_name: str):
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

    def __init__(self, name:str=None, description:str=None, choices:List[SlashOptionChoice]=None, required=True, **extra: ApplicationCommandOptionData) -> None:
        """
        Creates a slash command option. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-option-structure
        """
        self.data: ApplicationCommandOptionData = {}

        if description is None:
            description = "This option has no description. Sorry about that."

        # Check if all choices are same type.
        if choices is not None:
            allowed_type = type(choices[0]["value"])

            for choice in choices:
                if not type(choice["value"]) == allowed_type:
                    raise GoldyBotError("All choices got to have the same value type!")


        self.data["type"] = 3

        # If the choices are integer choices set the type of this slash option to 4.
        # This is because type 4 in the discord api means application options with integer choices and type 3 means application options with string choices, FUCK YOU DISCORD!
        # I didn't want to FUCKING have two separate SlashOption classes just for string choices and integer choices FUCK that, so I'm settling with this solution.
        if choices is not None:

            if isinstance(choices[0]["value"], int):
                self.data["type"] = 4


        self.data["name"] = name # If this is None it will get handled by the nextcore_utils.params_to_options() function respectively.
        self.data["description"] = description

        if choices is not None:
            self.data["choices"] = choices

        self.data["required"] = required

        self.data.update(extra)
        
        super().__init__(self.data)
