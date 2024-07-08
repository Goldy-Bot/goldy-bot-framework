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

    enable_group = group.group_command("enable")
    disable_group = group.group_command("disable")

    @enable_group.subcommand()
    @disable_group.subcommand()
    async def extension(self, platter: Platter, id: str):
        """Oh my god, I can't believe it."""
        await platter.send_message(f"👀 I see you, {platter.author.data['username']}!")

    @group.subcommand()
    async def enable_all_extension(self, platter: Platter, id: str):
        ...

    @group.subcommand() # TODO: Separate this into two sub commands.
    async def disable_extension(self, platter: Platter, id: str):
        ...

    @group.subcommand()
    async def disable_all_extension(self, platter: Platter, id: str):
        ...

    print(">>>", enable_group._master_command.data)


def load(goldy: Goldy):
    extension.mount(goldy, GuildConfig)
    return extension