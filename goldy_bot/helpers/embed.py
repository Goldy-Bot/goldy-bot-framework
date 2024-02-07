from __future__ import annotations
from typing import TYPE_CHECKING
from discord_typings import ( 
    EmbedData, 
    EmbedFieldData, 
    EmbedImageData, 
    EmbedFooterData, 
    EmbedAuthorData
)

if TYPE_CHECKING:
    from typing import Optional, List

import copy
import random
from ..colours import Colours
from .dict_helper import DictHelper

from GoldyBot import utils as legacy_utils

__all__ = (
    "EmbedAuthor", 
    "EmbedFooter", 
    "EmbedImage", 
    "EmbedField", 
    "Embed"
)

class EmbedAuthor(DictHelper[EmbedAuthorData]):
    """A class used to create an embed's author."""
    def __init__(
        self, 
        name: str, 
        url: Optional[str] = None, 
        icon_url: Optional[str] = None, 
        **kwargs
    ):
        data: EmbedAuthorData = {}

        data["name"] = name

        if url is not None:
            data["url"] = url

        if icon_url is not None:
            data["icon_url"] = icon_url

        super().__init__(data, **kwargs)

class EmbedFooter(DictHelper[EmbedFooterData]):
    """A class used to create an embed's footer."""
    def __init__(
        self, 
        text: str, 
        icon_url: Optional[str] = None, 
        **kwargs
    ):
        data: EmbedFooterData = {}

        data["text"] = text

        if icon_url is not None:
            data["icon_url"] = icon_url

        super().__init__(data, **kwargs)

class EmbedImage(DictHelper[EmbedImageData]):
    """A class used to add an image to a embed."""
    def __init__(
        self, 
        url: str, 
        height: Optional[int] = None, 
        width: Optional[int] = None, 
        **kwargs
    ):
        data: EmbedImageData = {}

        data["url"] = url

        if height is not None:
            data["height"] = height

        if width is not None:
            data["width"] = width

        super().__init__(data, **kwargs)

class EmbedField(DictHelper[EmbedFieldData]):
    """A class used to create an embed field for an embed."""
    def __init__(
        self, 
        name: str, 
        value: str, 
        inline: Optional[bool] = None, 
        **kwargs
    ):
        data: EmbedFieldData = {}

        data["name"] = name
        data["value"] = legacy_utils.line_fix(value)

        if inline is not None:
            data["inline"] = inline

        super().__init__(data, **kwargs)


class Embed(DictHelper[EmbedData]):
    """
    A class used to create a discord embed.
    
    -------------

    ⭐Example:
    -------------
    This is how you can create a simple Embed in goldy bot::

        await platter.send_message(
            "👋hello", reply=True, 
            embeds = [
                GoldyBot.Embed(title="OwO!", description="wow!", colour=Colours.AKI_PINK)
            ]
        )

    .. note::

        Don't forget to import ``from GoldyBot.nextcore_utils import Colours`` for colours.

    """
    def __init__(
        self, 
        title: Optional[str] = None, 
        description: Optional[str] = None, 
        fields: Optional[List[EmbedField]] = None, 
        colour: Optional[Colours] = None, 
        author: Optional[EmbedAuthor] = None, 
        footer: Optional[EmbedFooter] = None, 
        image: Optional[EmbedImage] = None, 
        thumbnail: Optional[EmbedImage] = None, 
        **kwargs
    ):
        data: EmbedData = {}

        if title is not None:
            data["title"] = title

        if description is not None:
            data["description"] = legacy_utils.line_fix(description)

        if fields is not None:
            data["fields"] = []

            for field in fields:
                data["fields"].append(field.data)

        if colour is None:
            colour = Colours.INVISIBLE

        data["color"] = colour.value

        if author is not None:
            data["author"] = author.data

        if footer is not None:
            data["footer"] = footer.data

        if image is not None:
            data["image"] = image.data

        if thumbnail is not None:
            data["thumbnail"] = thumbnail.data

        super().__init__(data, **kwargs)

    def format_title(self, **keys) -> None:
        "Just like the str.format() method but it formats the embed's title for you " \
        "so you can avoid the catastrophe at https://github.com/Goldy-Bot/Goldy-Bot-V5/issues/35."
        data = self.data

        data["title"] = data["title"].format(**keys)

        self.data.update(data)

    def format_description(self, **keys) -> None:
        "Just like the str.format() method but it formats the embed's description for you " \
        "so you can avoid the catastrophe at https://github.com/Goldy-Bot/Goldy-Bot-V5/issues/35."
        data = self.data

        data["description"] = data["description"].format(**keys)

        self.data.update(data)

    def format_fields(self, **keys) -> None:
        """
        Just like the str.format() method but it formats each of the embed's fields value.
        
        This was added because of https://github.com/Goldy-Bot/Goldy-Bot-V5/issues/35.
        """
        data = self.data

        for index, field in enumerate(data["fields"]):
            data["fields"][index]["value"] = field["value"].format(**keys)

        self.data.update(data)

    def set_image(self, image: EmbedImage) -> None: # NOTE: I might make this into an edit function of some sort if needed.
        """
        Set's an embed image.
        """
        self.data["image"] = image.data

    def set_random_footer(self, messages: List[str]) -> None:
        """
        Method that will randomly choose to display one of those messages in the footer; it can also choose to not display anything. 10% chance.
        """
        data = self.data

        if random.randint(0, 9) == 0:
            data["footer"] = {"text": random.choice(messages)}

        self.data.update(data)

    def copy(self) -> Embed: # TODO: Check if this works correctly. Might be safer to just pass the new dict to the embed's data attribute.
        """Returns copy of embed."""
        return Embed(**copy.deepcopy(self.data))