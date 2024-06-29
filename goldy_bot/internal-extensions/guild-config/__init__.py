import goldy_bot
from goldy_bot import Goldy, Platter

extension = goldy_bot.Extension("guild-config")

class GuildConfig():
    def __init__(self, goldy: Goldy):
        self.goldy = goldy

    group = extension.group_command(
        class_name = __qualname__, 
        name = "guild_config", 
        description = "🧰 Tune the goldy bot framework to your guild's needs."
    )

    @group.subcommand() # TODO: Separate this into two sub commands.
    async def enable_extension(self, platter: Platter, id: str):
        ...

    @group.subcommand()
    async def enable_all_extension(self, platter: Platter, id: str):
        ...

    @group.subcommand() # TODO: Separate this into two sub commands.
    async def disable_extension(self, platter: Platter, id: str):
        ...

    @group.subcommand()
    async def disable_all_extension(self, platter: Platter, id: str):
        ...


def load(goldy: Goldy):
    extension.mount(goldy, GuildConfig)
    return extension