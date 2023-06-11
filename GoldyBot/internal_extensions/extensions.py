import GoldyBot

class Extensions(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

    @GoldyBot.command()
    async def enable(self, platter: GoldyBot.GoldPlatter, extension: str):
        ...