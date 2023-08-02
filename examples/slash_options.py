import GoldyBot
from typing import List

# Need more help with creating extensions, visit our docs --> https://goldybot.devgoldy.xyz/goldy.extensions.html

from GoldyBot import SlashOption, SlashOptionChoice, SlashOptionAutoComplete

class Example(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

    # Slash option choices examples.
    # ------------------------------
    # Alright this is how it's done. Simple.

    @GoldyBot.command(slash_options = {
        "bear_name": SlashOption(
            description = "🐻 Pick a bear name.",
            choices = [
                "Simba",
                "Paddington",
                "Goldilocks",
                "Toto"
            ]
        )
    })
    async def bear_1(self, platter: GoldyBot.GoldPlatter, bear_name: str):
        if bear_name.lower() == "goldilocks":
            return await platter.send_message("*Goldilocks is not a bear you fool!*", reply=True)

        text = \
            "*> In the woods, there lived three bears in their cozy house. " \
            "There was a small wee bear, a middle-sized bear, " \
            f"and a great, huge bear known as* **{bear_name}**..." \

        await platter.send_message(text, reply=True)


    # CUSTOM RETURN VALUE
    # ====================
    # If you would like to the return value to differ you can use SlashOptionChoice class to alter that like so...
    @GoldyBot.command(slash_options = {
        "bear_number": SlashOption(
            name = "bear_name", # We can also force the slash option name to be something else than it is in our code.
            description = "🐻 Pick a bear name.",
            choices = [
                SlashOptionChoice(name="Simba", value=1),
                SlashOptionChoice(name="Paddington", value=2),
                SlashOptionChoice(name="Goldilocks", value=3),
                SlashOptionChoice(name="Toto", value=4)
            ]
        )
    })
    async def bear_2(self, platter: GoldyBot.GoldPlatter, bear_number: int):
        if bear_number == 3: # Goldilocks
            return await platter.send_message("*Goldilocks is not a bear you fool!*", reply=True)

        # but you know, why the hell would you want to do that in this type of command...
        elif bear_number == 1:
            bear_name = "Simba"
        elif bear_number == 2:
            bear_name = "Paddington"
        elif bear_number == 4:
            bear_name = "Toto"

        text = \
            "*> In the woods, there lived three bears in their cozy house. " \
            "There was a small wee bear, a middle-sized bear, " \
            f"and a great, huge bear known as* **{bear_name}**..." \

        await platter.send_message(text, reply=True)


    # AUTO COMPLETE
    # ==============
    # Okay but how about if I want to give the member a choice to use their own custom name.
    # Normal slash options wouldn't allow you to do this as they force you to pick the options that have already been set.
    # What you are looking for are auto complete slash options. You can use them like so...

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
    async def custom_bear_1(self, platter: GoldyBot.GoldPlatter, bear_name: str):
        if bear_name.lower() == "goldilocks":
            return await platter.send_message("*Goldilocks is not a bear you fool!*", reply=True)

        text = \
            "*> In the woods, there lived three bears in their cozy house. " \
            "There was a small wee bear, a middle-sized bear, " \
            f"and a great, huge bear known as* **{bear_name}**..." \

        await platter.send_message(text, reply=True)


    # CUSTOM AUTO COMPLETE
    # =====================
    # You can also override the callback and implement your own auto complete mechanism.
    # This can be very useful if you would like to perhaps perform things like web querying, there are so many possibilities.

    async def custom_auto_complete(self, member_typing_string: str) -> List[str]:
        # Perform your own custom auto completion shit.
        bear_names = ["Jeffery", "Simon", "Goldy", "Lisa", "Sam", "Goldilocks"]

        custom_choices = []
        for name in bear_names:

            if member_typing_string in name:
                custom_choices.append(name)

        # Return your custom choices.
        return custom_choices

    @GoldyBot.command(
        slash_options = {
            "bear_name": SlashOptionAutoComplete( # Now when you type these choices will be recommended to you but not forced on you.
                description = "⭐ Pick a custom bear name.",
                callback = custom_auto_complete
            )
        }
    )
    async def custom_bear_2(self, platter: GoldyBot.GoldPlatter, bear_name: str):
        if bear_name.lower() == "goldilocks":
            return await platter.send_message("*Goldilocks is not a bear you fool!*", reply=True)

        text = \
            "*> In the woods, there lived three bears in their cozy house. " \
            "There was a small wee bear, a middle-sized bear, " \
            f"and a great, huge bear known as* **{bear_name}**..." \

        await platter.send_message(text, reply=True)

def load():
    Example()