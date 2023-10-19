import GoldyBot
from GoldyBot import Colours

import nextcore

# TODO: Revamp the debug command.

class Debug(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

        self.debug_embed = GoldyBot.Embed(
            title = "🖤 Debug",
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
                    - DISK: ``{disk} MB/s``**
                    """,
                    inline = True
                ),
                GoldyBot.EmbedField(
                    name = "⚡ __Version:__",
                    value = """
                    **- GoldyBot: [``{version}``](https://github.com/Goldy-Bot/Goldy-Bot-V5)
                    - Nextcore: [``{nc_version}``](https://github.com/nextsnake/nextcore)
                    - Python: [``{py_version}``](https://www.python.org/)**
                    """,
                    inline = True
                )
            ],
            footer = GoldyBot.EmbedFooter("TODO: GIVE THIS COMMAND A MAKEOVER!!!! 🤬"),
            colour = Colours.BLACK,
            thumbnail = GoldyBot.EmbedImage(self.goldy.bot_user.avatar_url)
        )

    @GoldyBot.command(
        description = "🖤 Command for debugging the goldy bot framework.", 
        required_perms = [GoldyBot.Perms.BOT_DEV],
        hidden = True
    )
    async def debug(self, platter: GoldyBot.GoldPlatter):
        embed = self.debug_embed.copy()

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

load = lambda: Debug()