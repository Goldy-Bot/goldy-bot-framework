import GoldyBot
from GoldyBot import Colours

import nextcore

class Goldy(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

        self.goldy_embed = GoldyBot.Embed(
            title = "💛 Goldy Bot - Stats",
            fields = [
                GoldyBot.EmbedField(
                    name = "🗒️ __Stats:__", 
                    value = """
                    **- UpTime: {up_time}
                    - Guild Count: ``{guild_count}``**
                    """,
                    inline = False
                ),

                GoldyBot.EmbedField(
                    name = "📦 __Resources:__", 
                    value = """
                    **- Ping: ``{ping}``
                    - OS: ``{os}``
                    - CPU: ``{cpu}%``
                    - RAM: ``{ram} MB``
                    - DISK: ``{disk} MB/s``

                    [Made with {heart} By](https://github.com/Goldy-Bot/Goldy-Bot-V5) <@332592361307897856>**
                    """,
                    inline = True
                ),

                GoldyBot.EmbedField(
                    name = "⚡ __Version:__",
                    value = """
                    **- GoldyBot: ``{version}``
                    - Nextcore: ``{nc_version}``
                    - Python: ``{py_version}``**
                    """,
                    inline = True
                )
            ],
            colour = Colours.YELLOW,
            thumbnail = GoldyBot.EmbedImage(self.goldy.bot_user.avatar_url)
        )

    @GoldyBot.command(
        name="goldy", 
        description = "💛 Shows you stats about the current Goldy Bot framework instance.", 
        required_perms = [GoldyBot.Perms.BOT_DEV], # Umm, should we make this command available to bot admins too.
        hidden = True
    )
    async def goldy_cmd(self, platter: GoldyBot.GoldPlatter):
        embed = self.goldy_embed.copy()

        embed.format_fields(
            version = GoldyBot.info.VERSION,
            nc_version = nextcore.__version__,
            py_version = self.goldy.system.python_version,
            ping = (lambda x: "(Not Available Yet)" if x is None else f"{round(x * 1000, 2)}ms")(self.goldy.latency),
            os = (lambda x: x[:22] + "..." if len(x) >= 26 else x)(self.goldy.system.os),
            cpu = self.goldy.system.cpu,
            ram = self.goldy.system.ram,
            disk = self.goldy.system.disk,
            up_time = f"<t:{int(self.goldy.start_up_time.timestamp())}:R>",
            guild_count = len(self.goldy.guild_manager.guilds),

            heart = "🤍"
        )

        await platter.send_message(embeds=[embed], reply=True)


def load():
    Goldy()