import os
import psutil
import platform
import nextcore
import goldy_bot

from devgoldyutils import pprint

from GoldyBot.goldy import nextcore_utils as legacy_nextcore_utils

from goldy_bot import (
    Goldy, 
    Platter, 
    Colours, 
    Embed, 
    EmbedField, 
    EmbedFooter, 
    EmbedImage
)

extension = goldy_bot.Extension("debug")

class Debug():
    def __init__(self, goldy: Goldy):
        self.goldy = goldy

        self.debug_embed = Embed(
            title = "🖤 Debug",
            fields = [
                EmbedField(
                    name = "🗒️ __Stats:__", 
                    value = """
                    **- UpTime: {up_time}
                    - Guild Count: ``{guild_count}``**
                    """,
                    inline = False
                ),
                EmbedField(
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
                EmbedField(
                    name = "⚡ __Version:__",
                    value = """
                    **- GoldyBot: [``{version}``](https://github.com/Goldy-Bot/Goldy-Bot-V5)
                    - Nextcore: [``{nc_version}``](https://github.com/nextsnake/nextcore)
                    - Python: [``{py_version}``](https://www.python.org/)**
                    """,
                    inline = True
                )
            ],
            footer = EmbedFooter("TODO: GIVE THIS COMMAND A MAKEOVER!!!! 🤬"),
            colour = Colours.BLACK
        )

        self.process = psutil.Process(os.getpid())

    @extension.command(
        description = "🖤 Command for debugging the goldy bot framework."
    )
    async def debug(self, platter: Platter):
        embed = self.debug_embed.copy()

        bot_user = await self.goldy.low_level.get_bot_user_data()
        bot_avatar_url = bot_user.get("avatar")

        if bot_avatar_url is not None:
            embed.data["thumbnail"] = EmbedImage(
                url = legacy_nextcore_utils.DISCORD_CDN + f"avatars/{bot_user['id']}/{bot_avatar_url}.png?size=4096"
            ).data

        embed.format_fields(
            version = goldy_bot.__version__, 
            nc_version = nextcore.__version__, 
            py_version = platform.python_version(), 
            ping = (lambda x: "(Not Available Yet)" if x is None else f"{round(x * 1000, 2)}ms")(self.goldy.latency),
            os = (lambda x: x[:22] + "..." if len(x) >= 26 else x)(f"{platform.system()} {platform.release()}"), 
            cpu = self.process.cpu_percent(0) / psutil.cpu_count(), 
            ram = self.__convert_to_MB(self.process.memory_info().rss), 
            disk = "N/A", # TODO: Add this!
            up_time = f"<t:{int(self.goldy.boot_datetime.timestamp())}:R>", 
            guild_count = "N/A", # TODO: Add this!

            heart = "🥞"
        )

        await platter.send_message(embeds = [embed], reply = True)

    def __convert_to_MB(self, size):
        return (f"{size/float(1<<20):,.2f}")


def load(goldy: Goldy):
    extension.mount(goldy, Debug)
    return extension