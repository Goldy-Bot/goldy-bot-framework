import GoldyBot

# Need more help with creating extensions, visit our docs --> https://goldybot.devgoldy.xyz/goldy.extensions.html

class Example(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

    # Sub command example.
    # ----------------------
    @GoldyBot.command(group=True)
    async def game(self, platter: GoldyBot.GoldPlatter):
        if platter.author.id == "332592361307897856": # Replace this with your discord id and watch what happens.
            return True

        # You are able to perform checks with sub commands like this.
        # Returning False will stop the execution of the sub command. 
        # Returning True or nothing (None) will allow the sub command to execute.

        await platter.send_message(
            "You are not the game master! So you may not start the game.", reply=True
        )
        return False

    @game.sub_command()
    async def start(self, platter: GoldyBot.GoldPlatter):
        await platter.send_message("✅ Game has started!", reply=True)

    @game.sub_command()
    async def end(self, platter: GoldyBot.GoldPlatter):
        await platter.send_message("🟠 Game has ended!", reply=True)

def load():
    Example()