import platform
import nextcore
import goldy_bot
from devgoldyutils import LoggerAdapter

from GoldyBot.goldy import nextcore_utils as legacy_nextcore_utils

from goldy_bot import (
    Goldy, 
    Platter, 
    Colours, 
    Embed, 
    EmbedField, 
    EmbedImage
)

from goldy_bot.logger import goldy_bot_logger

logger = LoggerAdapter(goldy_bot_logger, prefix = "Debug")

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
                    **- GoldyBot: {icon} [``{version}``](https://github.com/Goldy-Bot/Goldy-Bot-Framework)
                    - Nextcore: [``{nc_version}``](https://github.com/nextsnake/nextcore)
                    - Python: [``{py_version}``](https://www.python.org/)**
                    """,
                    inline = True
                )
            ],
            colour = Colours.BLACK
        )

    @extension.command(
        description = "🖤 Command for debugging the goldy bot framework."
    )
    async def debug(self, platter: Platter):
        embed = self.debug_embed.copy()

        bot_user = await self.goldy.low_level.get_bot_user_data()
        bot_avatar_url = bot_user.get("avatar")

        if bot_avatar_url is not None:
            embed_image = EmbedImage(
                url = legacy_nextcore_utils.DISCORD_CDN + f"avatars/{bot_user['id']}/{bot_avatar_url}.png?size=4096"
            )

            embed.data["thumbnail"] = embed_image.data

        embed.format_fields(
            version = goldy_bot.__version__, 
            nc_version = nextcore.__version__, 
            py_version = platform.python_version(), 
            ping = (lambda x: "(Not Available Yet)" if x is None else f"{round(x * 1000, 2)}ms")(self.goldy.latency),
            os = (lambda x: x[:22] + "..." if len(x) >= 26 else x)(f"{platform.system()} {platform.release()}"), 
            cpu = self.goldy.cpu_usage, 
            ram = self.goldy.ram_usage, 
            disk = self.goldy.disk_usage, 
            up_time = f"<t:{int(self.goldy.boot_datetime.timestamp())}:R>", 
            guild_count = "N/A", # TODO: Add this!

            icon = "🥞"
        )

        await platter.send_message(embeds = [embed], reply = True)

def load(goldy: Goldy):
    # Don't load debug extension if not in dev mode present.
    if goldy.config.test_guild_id is None:
        logger.info("Debug extension will be disabled as you are not running in dev mode.")
        return None

    extension.mount(goldy, Debug)
    return extension