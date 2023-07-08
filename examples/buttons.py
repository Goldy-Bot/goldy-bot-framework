import GoldyBot
from GoldyBot import SlashOption, Button, ButtonStyle

import random

# Need more help with creating extensions, visit our docs --> https://goldybot.devgoldy.xyz/goldy.extensions.html

class Example(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

    # Buttons example.
    # ------------------
    @GoldyBot.command(
        description = "Have you ever wanted to 💣nuke a city? WELL FUCK IT, NOW YOU CAN!", 
        slash_options = {
            "city": SlashOption(
                description = "The 🏢 city you would like to 💣nuke!"
            )
        }
    )
    async def nuke(self, platter: GoldyBot.GoldPlatter, city: str):

        await platter.send_message(
            f"Are you sure you would like to nuke **{city}**?",
            recipes = [
                Button(ButtonStyle.GREEN, label="Yes", callback = self.nuke_city, city = city),
                Button(ButtonStyle.RED, label="No", callback = lambda x: x.send_message("👨‍🦱 Alright we're holding off captain."))
            ]
        )

    
    async def nuke_city(self, platter: GoldyBot.GoldPlatter, city: str):
        casualties = random.randint(800, 10000)

        await platter.send_message(
            f"> 💣 You nuked {city}, there were {casualties} casualties.",
            reply = True
        )

def load():
    Example()