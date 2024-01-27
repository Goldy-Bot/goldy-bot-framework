from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
    from discord_typings import UserData

    from ....typings import LowLevelSelfT

from nextcore.http import Route

__all__ = (
    "User",
)

class User():
    def __init__(self) -> None:
        super().__init__()

    async def get_bot_user_data(self: LowLevelSelfT[Self], **kwargs) -> UserData:
        self.logger.debug("Requesting bot user data...")

        r = await self.goldy.client.request(
            Route(
                "GET",
                "/users/@me"
            ),
            **self.goldy.key_and_headers,
            **kwargs
        )

        data = await r.json()
        return data