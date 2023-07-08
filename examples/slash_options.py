import GoldyBot
from GoldyBot import SlashOption, SlashOptionChoice

# Need more help with creating extensions, visit our docs --> https://goldybot.devgoldy.xyz/goldy.extensions.html

class Example(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

    # Slash option choices example.
    # ------------------------------
    @GoldyBot.command(slash_options = {
        "bear_name": SlashOption(
            description = "🐻 Pick a bear name.",
            choices = [
                SlashOptionChoice(name="Simba", value=1),
                SlashOptionChoice(name="Paddington", value=2),
                SlashOptionChoice(name="Goldilocks", value=3),
                SlashOptionChoice(name="Toto", value=4)
            ]
        )
    })
    async def bear(self, platter: GoldyBot.GoldPlatter, bear_name: int):
        if bear_name == "goldilocks":
            return await platter.send_message("*Goldilocks is not a bear you fool!*", reply=True)

        text = \
            "*> In the woods, there lived three bears in their cozy house. " \
            "There was a small wee bear, a middle-sized bear, " \
            f"and a great, huge bear known as* **{bear_name}**..." \

        await platter.send_message(text, reply=True)

def load():
    Example()