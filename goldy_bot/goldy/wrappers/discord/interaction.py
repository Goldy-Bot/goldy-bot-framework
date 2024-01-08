from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional
    from typing_extensions import Self

    from discord_typings import ApplicationCommandPayload, ApplicationCommandData

    from ....typings import GoldySelfT

from nextcore.http import Route

__all__ = (
    "Interaction",
)

class Interaction():
    def __init__(self) -> None:
        self.__previous_commands_payload: List[ApplicationCommandPayload] = []
        super().__init__()

    async def create_application_commands(
        self: GoldySelfT[Self], 
        payload: List[ApplicationCommandPayload], 
        guild_id: Optional[str] = None,
        force: bool = False
    ) -> List[ApplicationCommandData]:
        """
        Method that registers application commands with discord respecting already registered commands within the framework.

        If ``guild_id`` is set a guild application command will be registered instead.
        If ``force`` is set to True previously registered commands will be wiped as standard behavior when making the request to discord yourself.
        """
        created_commands: List[ApplicationCommandData] = []

        if payload == [] and force is False:
            return []

        if force is False:
            payload += [x for x in self.__previous_commands_payload if x not in payload]

        app_data = await self.get_application_data()

        self.logger.debug(f"Registering these commands --> {[x['name'] for x in payload]}")

        if guild_id is not None:
            self.logger.info("Registering guild commands...")

            r = await self.client.request(
                Route(
                    "PUT", 
                    "/applications/{application_id}/guilds/{guild_id}/commands",
                    application_id = app_data["id"],
                    guild_id = guild_id
                ),
                json = payload,
                **self.key_and_headers
            )

            created_commands = await r.json()

        else:
            self.logger.info("Registering global commands...")

            r = await self.client.request(
                Route(
                    "PUT", 
                    "/applications/{application_id}/commands",
                    application_id = app_data["id"]
                ),
                json = payload,
                **self.key_and_headers
            )

            created_commands = await r.json()

        self.__previous_commands_payload = payload

        return created_commands

    async def get_application_commands(
        self: GoldySelfT[Self], 
        guild_id: Optional[str] = None
    ) -> List[ApplicationCommandData]:

        app_data = await self.get_application_data()

        if guild_id is not None:
            self.logger.info("Registering guild commands...")

            r = await self.client.request(
                Route(
                    "GET", 
                    "/applications/{application_id}/guilds/{guild_id}/commands",
                    application_id = app_data["id"],
                    guild_id = guild_id
                ),
                **self.key_and_headers
            )

            data = await r.json()
            return data

        self.logger.info("Registering global commands...")

        r = await self.client.request(
            Route(
                "GET", 
                "/applications/{application_id}/commands",
                application_id = app_data["id"]
            ),
            **self.key_and_headers
        )

        data = await r.json()
        return data