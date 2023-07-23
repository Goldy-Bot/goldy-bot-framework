from __future__ import annotations

import GoldyBot
from GoldyBot import cache_lookup, Perms, info
from GoldyBot.goldy.extensions import extensions_cache

class GuildAdmin(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

        self.extension_enabled = GoldyBot.Embed(
            title = "💚 Enabled!",
            description = "The extension **[``{extension_name}``]({extension_url})** has been enabled. 👍",
            colour = GoldyBot.Colours.GREEN
        )

        self.extension_already_enabled = GoldyBot.Embed(
            title = "🧡 Already Enabled!",
            description = "That extension is already enabled.",
            colour = GoldyBot.Colours.AKI_ORANGE
        )

        self.all_extensions_enabled = GoldyBot.Embed(
            title = "💚 Enabled All Extensions!",
            description = "All extensions have been enabled. 👍",
            colour = GoldyBot.Colours.LIME_GREEN
        )

        self.all_extensions_disabled = GoldyBot.Embed(
            title = "🖤 Disabled All Extensions!",
            description = "All extensions have been disabled. 👍",
            colour = GoldyBot.Colours.BLACK
        )

        self.extension_disabled = GoldyBot.Embed(
            title = "❤️ Disabled!",
            description = "The extension **[``{extension_name}``]({extension_url})** has been disabled. 👍",
            colour = GoldyBot.Colours.RED
        )

        self.extension_already_disabled = GoldyBot.Embed(
            title = "🤎 Already Disabled!",
            description = "That extension is already disabled.",
            colour = GoldyBot.Colours.BROWN
        )

    admin = GoldyBot.GroupCommand("admin", required_perms = [Perms.GUILD_OWNER], hidden = True)

    @admin.sub_command(
        description = "🧰💚 A command for enabling a Goldy Bot extension in this guild.",
        slash_options = {
            "extension": GoldyBot.SlashOption(
                choices = [GoldyBot.SlashOptionChoice(extension[0], extension[0]) for extension in extensions_cache]
            )
        }
    )
    async def enable_extension(self, platter: GoldyBot.GoldPlatter, extension: str):
        guild_config = await platter.guild.config
        extension: GoldyBot.Extension = cache_lookup(extension, extensions_cache)[1]

        if extension.name in guild_config.allowed_extensions or guild_config.allowed_extensions == []:
            if extension.name not in guild_config.disallowed_extensions and not guild_config.disallowed_extensions == ["."]:
                await platter.send_message(embeds = [self.extension_already_enabled], hide = True)
                return

        disallowed = guild_config.disallowed_extensions
        if extension.name in disallowed:
            disallowed.remove(extension.name)

            await guild_config.push({
                "extensions": {
                    "disallowed": disallowed
                }
            })

        await guild_config.push({
            "extensions": {
                "allowed": guild_config.allowed_extensions + [extension.name]
            }
        })

        embed = self.extension_enabled.copy()

        embed.format_description(
            extension_name = extension.name,
            extension_url = extension.metadata.url if extension.metadata is not None else info.GITHUB_REPO
        )

        await platter.send_message(embeds = [embed], hide = True)

    @admin.sub_command(
        description = "🧰❤️ A command for disabling a Goldy Bot extension in this guild.",
        slash_options = {
            "extension": GoldyBot.SlashOption(
                choices = [GoldyBot.SlashOptionChoice(extension[0], extension[0]) for extension in extensions_cache]
            )
        }
    )
    async def disable_extension(self, platter: GoldyBot.GoldPlatter, extension: str):
        guild_config = await platter.guild.config
        extension: GoldyBot.Extension = cache_lookup(extension, extensions_cache)[1]

        if extension.name in guild_config.disallowed_extensions or guild_config.disallowed_extensions == ["."]:
            if extension.name not in guild_config.allowed_extensions:
                await platter.send_message(embeds = [self.extension_already_disabled], hide = True)
                return

        allowed = guild_config.allowed_extensions
        if extension.name in allowed:
            allowed.remove(extension.name)

            await guild_config.push({
                "extensions": {
                    "allowed": allowed
                }
            })

        await guild_config.push({
            "extensions": {
                "disallowed": guild_config.disallowed_extensions + [extension.name]
            }
        })

        embed = self.extension_disabled.copy()

        embed.format_description(
            extension_name = extension.name,
            extension_url = extension.metadata.url if extension.metadata is not None else info.GITHUB_REPO
        )

        await platter.send_message(embeds = [embed], hide = True)

    @admin.sub_command(
        description = "🧰🖤 A command for disabling all Goldy Bot extensions in this guild."
    )
    async def disable_all_extensions(self, platter: GoldyBot.GoldPlatter):
        guild_config = await platter.guild.config

        await guild_config.push({
            "extensions": {
                "disallowed": ["."],
                "allowed": []
            }
        })

        await platter.send_message(embeds = [self.all_extensions_disabled], hide = True)

    @admin.sub_command(
        description = "🧰💚 A command for enabling all Goldy Bot extensions in this guild."
    )
    async def enable_all_extensions(self, platter: GoldyBot.GoldPlatter):
        guild_config = await platter.guild.config

        await guild_config.push({
            "extensions": {
                "disallowed": [],
                "allowed": []
            }
        })

        await platter.send_message(embeds = [self.all_extensions_enabled], hide = True)


def load():
    GuildAdmin()