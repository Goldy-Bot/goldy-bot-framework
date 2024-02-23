from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
    from ....typings.objects import PlatterSelfT

from devgoldyutils import LoggerAdapter

from ...member.member import Member
from ....logger import goldy_bot_logger

__all__ = (
    "AuthorWrapper",
)

logger = LoggerAdapter(goldy_bot_logger, prefix = "AuthorWrapper")

class AuthorWrapper():
    def __init__(self: PlatterSelfT[Self]) -> None:
        self.author = Member(
            data = self.data["member"]["user"], 
            goldy = self.goldy, 
            guild_id = self.data["guild_id"]
        )

        super().__init__()