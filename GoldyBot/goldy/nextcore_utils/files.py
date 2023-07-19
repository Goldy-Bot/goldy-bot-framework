# I might mass change this in the future, so get ready for breaking changes. 🤣
from __future__ import annotations
from typing import Union

from io import FileIO, BytesIO

class File():
    """
    Goldy bot's basic file object.
    """
    def __init__(self, file: Union[FileIO, BytesIO], file_name: str) -> None:
        self.file_io = file

        self.name = file_name
        self.attachment_url = f"attachment://{file_name}"
        """Returns the attachment url string. Useful when attaching images to Embeds."""

    @property
    def contents(self) -> bytes:
        """Returns the contents of this file. Useful for uploading."""
        return self.file_io.getvalue()