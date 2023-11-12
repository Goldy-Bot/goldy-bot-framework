from __future__ import annotations
from typing import TYPE_CHECKING, Type
from typing_extensions import get_args

if TYPE_CHECKING:
    from discord_typings.gateway import GenericDispatchEvent

import inspect
from ... import errors, utils
from ..objects.member import Member
from ..extensions import extensions_cache
from .. import get_goldy_instance, goldy_bot_logger
from ..objects.platter.golden_platter import GoldPlatter

__all__ = ("event",)

def event(
    name: str = None
):
    """
    Register an event in Goldy Bot with this decorator.

    ---------------

    ⭐ Example:
    -------------
    This is how you register a event in GoldyBot::

        @GoldyBot.event()
        async def on_message(self, event: GoldyBot.MessageCreateEvent):
            print(event)

    """
    def decorate(func):
        def inner(func):
            goldy = get_goldy_instance()

            event_name = name

            if event_name is None:
                signature = inspect.signature(func)
                event_param = signature.parameters.get("event")

                if event_param is None:
                    raise errors.GoldyBotError("'event' parameter missing!")

                event_param_annotations = get_args(event_param.annotation)

                if len(event_param_annotations) > 0:
                    event_type: Type[GenericDispatchEvent] = event_param_annotations[1]
                    event_literal = get_args(get_args(event_type)[0])[0]
                    event_name = get_args(event_literal)[0]

            if event_name is None:
                raise errors.GoldyBotError(
                    f"'{func.__name__}' event was not specified. Please include either a event name or type hint event parameter with the appropriate discord_typings event."
                )

            goldy_bot_logger.info(f"Registering event '{event_name}' on '{func.__name__}' function...")

            async def event_callback(event):
                extension_name = str(func).split(" ")[1].split(".")[0]
                extension = utils.cache_lookup(extension_name, extensions_cache)[1]

                logger = extension.logger
                guild = goldy.guild_manager.get_guild(event["guild_id"])

                if guild is not None:
                    platter = GoldPlatter(
                        event, 
                        Member(event["author"], guild, goldy), 
                        None, 
                        goldy, 
                        logger
                    )

                    if extension.is_disabled:
                        return False

                    await guild.config_wrapper.update()

                    if await guild.is_extension_allowed(extension) is False:
                        return False

                    if await guild.do_extension_restrictions_pass(extension, platter) is False:
                        return False

                    await func(extension, event)

            goldy.shard_manager.event_dispatcher.add_listener(event_callback, event_name)
            return func

        return inner(func)

    return decorate