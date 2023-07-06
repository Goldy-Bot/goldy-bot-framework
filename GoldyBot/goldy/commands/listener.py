from __future__ import annotations

from typing import Tuple, TYPE_CHECKING
from devgoldyutils import Colours
from discord_typings import InteractionCreateData, MessageData, ApplicationCommandOptionInteractionData, ComponentInteractionData

from .command import Command
from .slash_command import SlashCommand
from .prefix_command import PrefixCommand
from ..recipes.buttons.button import Button
from ..nextcore_utils.slash_options.auto_complete.send import send_auto_complete
from .. import objects
from ... import LoggerAdapter, goldy_bot_logger, utils
from ..objects.platter.golden_platter import GoldPlatter
from ..objects.platter.silver_platter import SilverPlatter

if TYPE_CHECKING:
    from .. import Goldy

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
            self.on_interaction,
            event_name="INTERACTION_CREATE"
        )
        self.logger.info("Interaction listener set!")

        # Prefix command listener.
        self.goldy.shard_manager.event_dispatcher.add_listener(
            self.on_prefix_cmd,
            event_name="MESSAGE_CREATE"
        )
        self.logger.info("Prefix command listener set!")

        return None


    async def on_interaction(self, interaction: InteractionCreateData) -> None:
        guild = self.goldy.guild_manager.get_guild(interaction["guild_id"])

        if guild is not None:
            await guild.update()

            author = objects.Member(interaction["member"]["user"], guild, self.goldy)

            # Slash command.
            # ---------------
            if interaction["type"] == 2:
                command: Tuple[str, SlashCommand] = utils.cache_lookup(interaction["data"]["id"], self.goldy.invokables)

                if command is not None:
                    gold_platter = GoldPlatter(
                        data = interaction, 
                        author = author,
                        command = command[1]
                    )

                    await command[1].invoke(
                        gold_platter
                    )


            # Message components.
            # --------------------
            elif interaction["type"] == 3:
                interaction: ComponentInteractionData
                message_component: Tuple[str, Button] = utils.cache_lookup(interaction["data"]["custom_id"], self.goldy.invokables)

                if message_component is not None:
                    silver_platter = SilverPlatter(
                        data = interaction, 
                        author = author,
                        recipe = message_component[1]
                    )

                    await message_component[1].invoke(
                        silver_platter
                    )


            # Command auto complete
            # -----------------------
            elif interaction["type"] == 4:
                command: Tuple[str, Command] = utils.cache_lookup(interaction["data"]["name"], self.goldy.invokables)

                current_typing_option: ApplicationCommandOptionInteractionData = None

                for option in interaction["data"]["options"]:
                    if option.get("focused"):
                        current_typing_option = option
                        break

                if command is not None:
                    await send_auto_complete(
                        data = interaction,
                        goldy = self.goldy,
                        current_typing_option = current_typing_option,
                        command = command[1]
                    )

        return None


    async def on_prefix_cmd(self, message: MessageData) -> None:
        guild = self.goldy.guild_manager.get_guild(message["guild_id"])

        # If user is bot return right away.
        if message["author"].get("bot", False):
            return

        if guild is not None:
            #await guild.update() # Since v5.0dev5 the guild database data is no longer updated automatically on message event.
            # This means if you manually change the command prefix in the database you have to also manually run "reload_config" in live console.
            
            # Check if prefix is correct.
            if not guild.prefix == message["content"][0]:
                return
            
            # i really hope this doesn't break
            command: Tuple[str, PrefixCommand] = utils.cache_lookup(message["content"].split(" ")[0][1:], self.goldy.invokables)

            if command is not None: # TODO: move this to invoke method and add a front end exception.
                gold_platter = GoldPlatter(
                    data = message, 
                    author = objects.Member(message["author"], guild, self.goldy),
                    command = command[1],
                )
                
                await command[1].invoke(
                    gold_platter
                )
        
        return None
