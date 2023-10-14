from __future__ import annotations
from typing import TYPE_CHECKING, get_args, Literal, Type

if TYPE_CHECKING:
    from discord_typings.gateway import GenericDispatchEvent

import inspect
from ... import errors, utils
from .. import get_goldy_instance
from ..extensions import extensions_cache, Extension

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
                    event_type: Type[GenericDispatchEvent] = event_param_annotations[0]
                    event_literal = get_args(get_args(event_type)[0])[0]
                    event_name = get_args(event_literal)[0]

            if event_name is None:
                raise errors.GoldyBotError(
                    f"'{func.__name__}' event was not specified. Please include either a event name or type hint event parameter with the appropriate discord_typings event."
                )

            extension_name = str(func).split(" ")[1].split(".")[0]
            extension: Extension = utils.cache_lookup(extension_name, extensions_cache)

            goldy.shard_manager.event_dispatcher.add_listener(lambda x: func(extension, x), event_name)

            return func

        return inner(func)

    return decorate