import GoldyBot

# Need more help with creating extensions, visit our docs --> https://goldybot.devgoldy.xyz/goldy.extensions.html

class Example(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

    @GoldyBot.command()
    async def hello(self, platter: GoldyBot.GoldPlatter):
        await platter.send_message("👋hello", reply=True)

def load():
    Example()