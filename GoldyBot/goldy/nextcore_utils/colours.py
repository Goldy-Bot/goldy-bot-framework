from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .files import File

from colorthief import ColorThief
from enum import Enum

class Colours(Enum):
    """Goldy bot v4 colours ported over to v5 with some added colours."""
    AKI_PINK = 0xFF1493
    AKI_ORANGE = 0xF4900C
    AKI_RED = 0xff0051
    AKI_BLUE = 0X75E6DA
    BLUE = 0x3061f2
    GREEN = 0x00FF00
    LIME_GREEN = 0x8AFF65
    YELLOW = 0xffff4d
    PURPLE = 0xFF00FF
    RED = 0xFF0000
    BROWN = 0xFFBA6D
    GREY = 0x3B3B3B
    WHITE = 0xFFFFFF
    BLACK = 0x000000

    INVISIBLE = 0x2B2D31
    """Makes the embed colour the same as the background essentially giving the embed colour a transparent look."""

    def __init__(self, colour: int):
        ...

    @classmethod
    def from_rgb(cls, r: int, g:int, b:int) -> int:
        """Converts rgb values into colour."""
        return (r << 16) + (g << 8) + b

    @classmethod
    def from_image(cls, file: File, accuracy: int = 5) -> int:
        """Returns the dominant colour in that image."""
        r, g, b = ColorThief(file.file_io).get_color(accuracy)
        return cls.from_rgb(r, g, b)