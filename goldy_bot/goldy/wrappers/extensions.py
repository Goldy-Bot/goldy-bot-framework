from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

    from ..goldy import Goldy
    from ...extensions import Extension

from .wrapper import Wrapper

class ExtensionsWrapper(Wrapper):
    """Brings valuable methods to the goldy class for managing extensions."""
    def __init__(self, goldy: Goldy) -> None:
        self.__goldy = goldy

        self.extensions: List[Extension] = []

    def add_extension(self, extension: Extension) -> None:
        """Method to add an extension to the framework."""
        self.extensions.append(extension)

        self.__goldy.logger.info(
            f"The extension '{extension.name}' has been added!"
        )