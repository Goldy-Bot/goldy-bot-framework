from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_typings import UserData

    from ...goldy import Goldy

from nextcore.http import Route

__all__ = (
    "User",
)

class User():
    def __init__(self) -> None:
        super().__init__()

    async def get_bot_user_data(self: Goldy, **kwargs) -> UserData:
        self.logger.debug("Requesting bot user data...")

        r = await self.client.request(
            Route(
                "GET",
                "/users/@me"
            ),
            **self.key_and_headers,
            **kwargs
        )

        data = await r.json()
        return data