from __future__ import annotations

from typing import List, Literal
from discord_typings import ApplicationCommandOptionData
from discord_typings.interactions.commands import StrCommandOptionChoiceData, IntCommandOptionChoiceData

class SlashOptionChoice(dict):
    """A class used to create slash option choice."""
    def __init__(self, name:str, value: str|int, **extra):
        """
        Creates an slash option choice. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-option-choice-structure
        """
        self.data: StrCommandOptionChoiceData | IntCommandOptionChoiceData = {}

        self.type: Literal["string"] | Literal["integer"] = "string"

        if isinstance(value, int):
            self.type = "integer"

        self.data["name"] = name
        self.data["value"] = value

        self.data.update(extra)

        super().__init__(self.data)
        

class SlashOption(dict):
    """
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
        async def bear(self, platter: GoldyBot.GoldenPlatter, bear_name):
            if bear_name == "goldilocks":
                return await platter.send_message("Goldilocks is not a bear you fool!", reply=True)

            text = f'''
    > Once upon a time there were three bears, who lived together in a house of their own in the woods. 
    > One of them was a little, small wee bear; one was a middle-sized bear, and the other was a great, huge bear named **{bear_name.title()}**...
            '''
            
            await platter.send_message(text, reply=True)

    """

    def __init__(self, name:str=None, description:str=None, choices:List[SlashOptionChoice]=None, **extra: ApplicationCommandOptionData) -> None:
        """
        Creates a slash command option. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-option-structure
        """
        self.data: ApplicationCommandOptionData = {}

        if description is None:
            description = "This option has no description. Sorry about that."
        

        self.data["type"] = 3

        # If the choices are integer choices set the type of this slash option to 4.
        # This is because type 4 in the discord api means application options with integer choices and type 3 means application options with string choices, FUCK YOU DISCORD!
        # I didn't want to FUCKING have two separate SlashOption classes just for string choices and integer choices so I settled with this messy solution.
        if choices is not None:

            if choices[0].type == "integer":
                self.data["type"] = 4


        self.data["name"] = name # If this is None it will get handled by the nextcore_utils.params_to_options() function respectively.
        self.data["description"] = description

        if choices is not None:
            self.data["choices"] = choices

        self.data.update(extra)
        
        super().__init__(self.data)

