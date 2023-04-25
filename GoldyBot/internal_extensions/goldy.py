import GoldyBot
from GoldyBot import Colours

import nextcore

class Goldy(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

        self.goldy_embed = GoldyBot.Embed(
            title = "💛 Goldy Bot - Stats",
            description = """
            ***__Version:__*
            • GoldyBot: ``{version}``
            • Nextcore: ``{nc_version}``
            • Python: ``{py_version}``

            *__Resources:__*
            • Ping: ``{ping}``
            • OS: ``{os}``
            • CPU: ``{cpu}%``
            • RAM: ``{ram} GB``
            • DISK: ``{disk} MB/s``

            *Developed with {heart} By <@332592361307897856>***
            """,
            colour = Colours.YELLOW,
            thumbnail = GoldyBot.EmbedImage(self.goldy.bot_user.avatar_url)
        )
    
    @GoldyBot.command(name="goldy", description="💛 Shows you stats about the current Goldy Bot framework instance.")
    async def goldy_cmd(self, platter: GoldyBot.GoldPlatter):
        embed = self.goldy_embed.copy()

        embed["description"] = embed["description"].format(
            version = GoldyBot.info.VERSION,
            nc_version = nextcore.__version__,
            py_version = self.goldy.system.python_version,
            ping = (lambda x: "(Not Available)" if x is None else f"{round(x * 1000, 2)}ms")(self.goldy.latency),
            os = self.goldy.system.os,
            cpu = self.goldy.system.cpu,
            ram = self.goldy.system.ram,
            disk = self.goldy.system.disk,

            heart = "🤍"
        )

        await platter.send_message(embeds=[embed], reply=True)


def load():
    Goldy()