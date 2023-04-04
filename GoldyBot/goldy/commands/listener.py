from typing import Tuple
from devgoldyutils import Colours
from discord_typings import InteractionCreateData, MessageData

from . import commands_cache, Command
from .. import utils, objects, Goldy
from ... import LoggerAdapter, goldy_bot_logger

class CommandListener():
    """Class that handles the invoking of commands."""
    def __init__(self, goldy: Goldy) -> None:
        self.goldy = goldy

        self.logger = LoggerAdapter(goldy_bot_logger, prefix=Colours.BLUE.apply("CommandListener"))

    async def start_listening(self) -> None:
        """Registers nextcore listeners and starts listening for commands."""

        # Slash command listener.
        # ------------------------
        self.goldy.shard_manager.event_dispatcher.add_listener(
            self.on_slash_cmd,
            event_name="INTERACTION_CREATE"
        )
        self.logger.info("Slash command listener set!")

        # Prefix command listener.
        self.goldy.shard_manager.event_dispatcher.add_listener(
            self.on_prefix_cmd,
            event_name="MESSAGE_CREATE"
        )
        self.logger.info("Prefix command listener set!")

        return None


    async def on_slash_cmd(self, interaction: InteractionCreateData) -> None:
        # Only respond to slash command interactions.
        if not interaction["type"] == 2:
            return

        guild = self.goldy.guilds.get_guild(interaction["guild_id"])

        if guild is not None:

            command:Tuple[str, Command] = utils.cache_lookup(interaction["data"]["name"], commands_cache)

            if command is not None:
                await command[1].invoke(
                    data = interaction, 
                    type = objects.PlatterType.SLASH_CMD
                )

        return None


    async def on_prefix_cmd(self, message: MessageData) -> None:
        guild = self.goldy.guilds.get_guild(message["guild_id"])

        if guild is not None:
            # Check if prefix is correct.
            if not guild.prefix == message["content"][0]:
                return
            
            # i really hope this doesn't break
            command:Tuple[str, Command] = utils.cache_lookup(message["content"].split(" ")[0][1:], commands_cache)

            if command is not None:

                if command[1].allow_prefix_cmd:
                    # TODO: Add error handling for the TypeErrors that can occur here due to missing parameters.
                    await command[1].invoke(
                        data = message, 
                        type = objects.PlatterType.PREFIX_CMD
                    )

        return None