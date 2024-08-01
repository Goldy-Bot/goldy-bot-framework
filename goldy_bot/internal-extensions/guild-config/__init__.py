from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Tuple, Optional, Any

import goldy_bot
from goldy_bot import Goldy, Platter, SlashOptionAutoComplete, SlashOptionChoice

extension = goldy_bot.Extension("guild-config")

class GuildConfig():
    def __init__(self, goldy: Goldy):
        self.goldy = goldy

        self.list_of_config_keys: Optional[Tuple[str, type]] = None

    async def get_keys(self, typing_value: str, **_) -> List[SlashOptionChoice]:
        return [
            SlashOptionChoice(key, key) for key, _ in self._get_config_keys() if typing_value in key
        ]

    async def get_values(self, typing_value: str, key: str, **_) -> List[SlashOptionChoice]:
        config_key_data_type = str

        for config_key, data_type in self._get_config_keys():

            if config_key == key:
                config_key_data_type = data_type

        options = []

        if config_key_data_type == bool:
            options = [
                SlashOptionChoice("true", True), 
                SlashOptionChoice("false", False)
            ]

        print(">>", options)

        return options

    @extension.command(
        description = "🧰 Tune the goldy bot framework to your guild's needs.",
        slash_options = {
            "key": SlashOptionAutoComplete(
                callback = get_keys
            ),
            "value": SlashOptionAutoComplete(
                callback = get_values
            )
        }
    )
    async def guild_config(self, platter: Platter, key: str, value: Any):
        guild = await platter.guild
        guild_database_wrapper = await guild.database

        if key not in [key for key, _ in self._get_config_keys()]:
            platter.error(
                message = "This config key is not valid! Are you sure you typed it correctly?",
                title = "🧡 Config KEY invalid!"
            )

        guild_configs: dict = guild_database_wrapper.get("configs", {})

        guild_configs[key] = value

        await guild_database_wrapper.push(
            data = {
                "configs": guild_configs
            }
        )

        await platter.send_message(f"*Successfully set config `{key}` to `{value}`*!", hidden = True)

    def _get_config_keys(self) -> List[Tuple[str, type]]:
        if self.list_of_config_keys is None:
            list_of_keys = []

            for extension in self.goldy.extensions:
                list_of_keys.append((f"extensions.{extension.name}.allow", bool))

            self.list_of_config_keys = list_of_keys

        return self.list_of_config_keys


def load(goldy: Goldy):
    extension.mount(goldy, GuildConfig)
    return extension