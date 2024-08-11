from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Tuple, Optional, TypeVar

    T = TypeVar("T", str)

import goldy_bot
from goldy_bot import Goldy, Platter, SlashOptionAutoComplete, SlashOptionChoice
from goldy_bot.requirements import  is_guild_owner

extension = goldy_bot.Extension("guild-config")

class GuildConfig():
    def __init__(self, goldy: Goldy):
        self.goldy = goldy

        self.list_of_config_keys: Optional[Tuple[str, type]] = None

    group = extension.group_command(
        class_name = __qualname__, 
        name = "guild_config", 
        description = "🧰 Tune the goldy bot framework to your guild's needs."
    )

    @group.master_command()
    async def handle_invalid_key(self, platter: Platter, key: str, **kwargs):

        if key not in [key for key, _ in self.__get_config_keys()]:
            platter.error(
                message = "This config key is not valid! Are you sure you typed it correctly?",
                title = "🧡 Config KEY invalid!"
            )

    async def get_keys(self, typing_value: str, **_) -> List[SlashOptionChoice]:
        return [
            SlashOptionChoice(key, key) for key, _ in self.__get_config_keys() if typing_value in key
        ]

    async def get_values(self, typing_value: str, key: str, **_) -> List[SlashOptionChoice]:
        config_key_data_type = str

        for config_key, data_type in self.__get_config_keys():

            if config_key == key:
                config_key_data_type = data_type

        options = []

        if config_key_data_type is bool:
            options = [
                SlashOptionChoice("true", "true"), 
                SlashOptionChoice("false", "false")
            ]

        return options

    @group.subcommand(
        name = "set", 
        description = "Change / Set guild configuration.", 
        slash_options = {
            "key": SlashOptionAutoComplete(
                callback = get_keys
            ),
            "value": SlashOptionAutoComplete(
                callback = get_values
            )
        },
        requirements = [is_guild_owner()]
    )
    async def set_guild_config(self, platter: Platter, key: str, value: str):
        guild = await platter.guild
        guild_database_wrapper = await guild.database

        guild_configs: dict = guild_database_wrapper.get("configs", {})

        value = self.__parse_value_or_error(platter, value, key)

        guild_configs[key] = value

        await guild_database_wrapper.push(
            data = {
                "configs": guild_configs
            }
        )

        await platter.send_message(
            f"💚 **Successfully** set guild config `{key}` to **`{value}`**!", 
            hidden = True
        )

    @group.subcommand(
        name = "view", 
        description = "Change / Set guild configuration.", 
        slash_options = {
            "key": SlashOptionAutoComplete(
                callback = get_keys
            )
        },
        requirements = [is_guild_owner()]
    )
    async def view_guild_config(self, platter: Platter, key: str):
        guild = await platter.guild
        guild_database_wrapper = await guild.database

        guild_configs: dict = guild_database_wrapper.get("configs", {})

        await platter.send_message(
            f"➡️ `{key}` is set to **`{guild_configs.get(key, 'None')}`**.", 
            hidden = True
        )

    def __get_config_keys(self) -> List[Tuple[str, type]]:
        if self.list_of_config_keys is None:
            list_of_keys = []

            for extension in self.goldy.extensions:
                if extension.internal:
                    continue

                list_of_keys.append((f"extensions.{extension.name}.allow", bool))

            self.list_of_config_keys = list_of_keys

        return self.list_of_config_keys

    def __parse_value_or_error(self, platter: Platter, value: T, key: str) -> T | bool:
        _type = None

        for config_key, config_type in self.__get_config_keys():

            if config_key == key:
                _type = config_type
                break

        if _type is bool:

            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            else:
                platter.error(
                    message = "The value you've entered is not a boolean!",
                    title = "🧡 Incorrect value entered!"
                )

        return value


def load(goldy: Goldy):
    extension.mount(goldy, GuildConfig)
    return extension