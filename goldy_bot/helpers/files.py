from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, BinaryIO
    from typing_extensions import Self

import os
import io
import aiohttp
import requests
from ..errors import GoldyBotError

__all__ = (
    "File",
)

class File():
    """
    Goldy bot's basic file object for 🥞 pancake.
    """
    def __init__(self, file: BinaryIO, file_name: Optional[str] = None) -> None:
        self.file = file

        try:
            self.name = file_name or os.path.split(file.name)[1]
        except AttributeError as e:
            raise GoldyBotError(
                f"This file object does not have the .name attribute, 'file_name' must be specified! Error >> {e}"
            )

        self.attachment_url = f"attachment://{file_name}"
        """Returns the attachment url string. Useful when attaching images to Embeds."""

    @classmethod
    async def from_response(cls, response: requests.Response | aiohttp.ClientResponse) -> Self:
        """Supports response objects from requests and aiohttp."""
        content_type = response.headers.get("Content-Type")

        if content_type is None:
            raise GoldyBotError("'response' does not have 'Content-Type' header!")

        content = None

        if isinstance(response, requests.Response):
            content = response.content
        elif isinstance(response, aiohttp.ClientResponse):
            content = await response.read()

        return cls(
            file = io.BytesIO(content), 
            file_name = f"image.{content_type.split('/')[1]}"
        )

    @property
    def contents(self) -> bytes:
        """Returns the contents of this file. Useful for uploading."""
        self.file.seek(0)
        return self.file.read()

    def close(self) -> None:
        """Closes the mf."""
        self.file.close()