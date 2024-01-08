from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from typing_extensions import Self

    from discord_typings import ApplicationData

    from ....typings import GoldySelfT

from nextcore.http import Route

__all__ = (
    "Application",
)

class Application():
    def __init__(self) -> None:
        self.__application_data: Optional[ApplicationData] = None

        super().__init__()

    async def get_application_data(self: GoldySelfT[Self], **kwargs) -> ApplicationData:
        if self.__application_data is None:
            self.__application_data = self.get_cache("application_data")

        if self.__application_data is None:
            self.logger.debug("Requesting application data as it doesn't exist...")

            r = await self.client.request(
                Route(
                    "GET",
                    "/applications/@me"
                ),
                **self.key_and_headers,
                **kwargs
            )

            data = await r.json()
            self.__application_data = self.set_cache("application_data", data)

        return self.__application_data