import discord_typings
from typing_extensions import Annotated, Type

__all__ = ("MessageEvent",)

MessageEvent = Annotated[discord_typings.MessageData, Type[discord_typings.MessageCreateEvent]]