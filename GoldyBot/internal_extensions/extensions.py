from __future__ import annotations

import GoldyBot
from GoldyBot import cache_lookup, Perms
from GoldyBot.goldy.extensions import extensions_cache

class Extensions(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

        self.extension_enabled = GoldyBot.Embed(
            title = "💚 Enabled!",
            description = "Extension has been enabled. 👍",
            colour = GoldyBot.Colours.LIME_GREEN
        )

        self.extension_already_enabled = GoldyBot.Embed(
            title = "🧡 Already Enabled!",
            description = "That extension is already enabled.",
            colour = GoldyBot.Colours.AKI_ORANGE
        )

        self.extension_disabled = GoldyBot.Embed(
            title = "🖤 Disabled!",
            description = "Extension has been disabled. 👍",
            colour = GoldyBot.Colours.INVISIBLE # TODO: Replace this with black.
        )

        self.extension_already_disabled = GoldyBot.Embed(
            title = "🤎 Already Disabled!",
            description = "That extension is already disabled.",
            colour = GoldyBot.Colours.GREY # TODO: Replace this with brown.
        )

    extensions = GoldyBot.GroupCommand("extensions", hidden=True, required_roles = [Perms.BOT_DEV])

    @extensions.sub_command(
        description = "A command for enabling a Goldy Bot extension that is disabled.",
        slash_options = {
            "extension": GoldyBot.SlashOption(
                choices = [GoldyBot.SlashOptionChoice(extension[0], extension[0]) for extension in extensions_cache]
            )
        }
    )
    async def enable(self, platter: GoldyBot.GoldPlatter, extension: str):
        extension: GoldyBot.Extension = cache_lookup(extension, extensions_cache)[1]

        if not extension.is_disabled:
            await platter.send_message(embeds = [self.extension_already_enabled], delete_after = 5)
            return

        extension.enable()
        await platter.send_message(embeds = [self.extension_enabled])

    @extensions.sub_command(
        description = "A command for disabling a Goldy Bot extension that is enabled.",
        slash_options = {
            "extension": GoldyBot.SlashOption(
                choices = [GoldyBot.SlashOptionChoice(extension[0], extension[0]) for extension in extensions_cache]
            )
        }
    )
    async def disable(self, platter: GoldyBot.GoldPlatter, extension: str):
        extension: GoldyBot.Extension = cache_lookup(extension, extensions_cache)[1]

        if extension.is_disabled:
            await platter.send_message(embeds = [self.extension_already_disabled], delete_after = 5)
            return

        extension.disable()
        await platter.send_message(embeds = [self.extension_disabled])

def load():
    Extensions()