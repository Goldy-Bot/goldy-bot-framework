from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
    from typing import List, Optional, Dict

    from discord_typings import (
        InteractionMessageCallbackData,
        ApplicationCommandPayload, 
        ApplicationCommandData, 
        MessageData
    )

    from ....helpers import File
    from ....typings import LowLevelSelfT

from aiohttp import FormData
from nextcore.http import Route
from nextcore.common import json_dumps

__all__ = (
    "Interaction",
)

class Interaction():
    def __init__(self) -> None:
        self.__previous_commands_payload: List[ApplicationCommandPayload] = []
        super().__init__()

    async def create_application_commands(
        self: LowLevelSelfT[Self], 
        payload: List[ApplicationCommandPayload], 
        guild_id: Optional[str] = None,
        force: bool = False
    ) -> List[ApplicationCommandData]:
        """
        Method that registers application commands with discord respecting already registered commands within the framework.

        If ``guild_id`` is set a guild application command will be registered instead.
        If ``force`` is set to True previously registered commands will be wiped as standard behavior when making this request manually to discord.
        """
        created_commands: List[ApplicationCommandData] = []

        if payload == [] and force is False:
            return []

        if payload == self.__previous_commands_payload and force is False:
            return []

        if force is False:
            payload += [x for x in self.__previous_commands_payload if x not in payload]

        app_data = await self.get_application_data()

        self.logger.debug(f"Registering these commands --> {[x['name'] for x in payload]}")

        if guild_id is not None:
            self.logger.debug(f"Registering guild commands for '{guild_id}'...")

            r = await self.goldy.client.request(
                Route(
                    "PUT", 
                    "/applications/{application_id}/guilds/{guild_id}/commands",
                    application_id = app_data["id"],
                    guild_id = guild_id
                ),
                json = payload,
                **self.goldy.key_and_headers
            )

            created_commands = await r.json()

        else:
            self.logger.debug("Registering global commands...")

            r = await self.goldy.client.request(
                Route(
                    "PUT", 
                    "/applications/{application_id}/commands",
                    application_id = app_data["id"]
                ),
                json = payload,
                **self.goldy.key_and_headers
            )

            created_commands = await r.json()

        self.__previous_commands_payload = payload
        return created_commands

    async def get_application_commands(
        self: LowLevelSelfT[Self], 
        guild_id: Optional[str] = None
    ) -> List[ApplicationCommandData]:

        app_data = await self.get_application_data()

        if guild_id is not None:
            self.logger.debug("Getting guild application commands...")

            r = await self.goldy.client.request(
                Route(
                    "GET", 
                    "/applications/{application_id}/guilds/{guild_id}/commands",
                    application_id = app_data["id"],
                    guild_id = guild_id
                ),
                **self.goldy.key_and_headers
            )

            data = await r.json()
            return data

        self.logger.debug("Getting global application commands...")

        r = await self.goldy.client.request(
            Route(
                "GET", 
                "/applications/{application_id}/commands",
                application_id = app_data["id"]
            ),
            **self.goldy.key_and_headers
        )

        data = await r.json()
        return data

    async def get_interaction_message(self: LowLevelSelfT[Self], interaction_token: str) -> MessageData:
        """Get's the message data of the original interaction response."""
        app_data = await self.get_application_data()

        r = await self.goldy.client.request(
            Route(
                "GET", 
                "/webhooks/{application_id}/{interaction_token}/messages/@original", 
                application_id = app_data["id"], 
                interaction_token = interaction_token
            ),
            rate_limit_key = self.goldy.key_and_headers["rate_limit_key"]
        )

        data = await r.json()
        return data

    async def send_interaction_callback(
        self: LowLevelSelfT[Self], 
        interaction_id: str, 
        interaction_token: str, 
        payload: InteractionMessageCallbackData, 
        files: Optional[List[File]] = None
    ) -> None:
        form_data = FormData()

        if files is not None:

            for file in files:
                form_data.add_field(**self.__file_to_form_field(file))

        form_data.add_field(
            "payload_json", json_dumps(
                {
                    "type": 4, 
                    "data": payload
                }
            )
        )

        await self.goldy.client.request( 
            Route(
                "POST", 
                "/interactions/{interaction_id}/{interaction_token}/callback", 
                interaction_id = interaction_id, 
                interaction_token = interaction_token
            ),
            rate_limit_key = self.goldy.key_and_headers["rate_limit_key"],
            data = form_data
        )

    async def send_interaction_follow_up(
        self: LowLevelSelfT[Self], 
        interaction_token: str, 
        payload: InteractionMessageCallbackData, 
        files: Optional[List[File]] = None
    ) -> MessageData:
        form_data = FormData()
        app_data = await self.get_application_data()

        if files is not None:

            for file in files:
                form_data.add_field(**self.__file_to_form_field(file))

        form_data.add_field(
            "payload_json", json_dumps(payload)
        )

        r = await self.goldy.client.request( 
            Route(
                "POST", 
                "/webhooks/{application_id}/{interaction_token}", 
                application_id = app_data["id"], 
                interaction_token = interaction_token
            ),
            rate_limit_key = self.goldy.key_and_headers["rate_limit_key"],
            data = form_data
        )

        message_data = await r.json()
        return message_data

    def __file_to_form_field(self, file: File) -> Dict[str, str]:
        return {
            "name": file.name.split(".")[-2], 
            "value": file.contents,
            "filename": file.name
        }