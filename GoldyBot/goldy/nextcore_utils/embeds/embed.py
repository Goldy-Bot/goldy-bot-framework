from __future__ import annotations
from typing import List
from discord_typings import EmbedData, EmbedFieldData, EmbedImageData, EmbedFooterData

import copy
from ..colours import Colours
from .... import utils

class EmbedFooter(dict):
    """A class used to create an embed's footer."""
    def __init__(self, text: str, icon_url: str = None, proxy_icon_url: str = None, **extra) -> EmbedFooterData:
        """
        Creates an embed footer.
        """
        data: EmbedFooterData = {}

        data["text"] = text

        if icon_url is not None:
            data["icon_url"] = icon_url

        if proxy_icon_url is not None:
            data["proxy_icon_url"] = proxy_icon_url

        data.update(extra)

        super().__init__(data)

class EmbedImage(dict):
    """A class used to add an image to a embed."""
    def __init__(self, url: str, proxy_url: str = None, height: int = None, width: int = None, **extra) -> EmbedImageData:
        """
        Creates an embed image or thumbnail.
        """
        data: EmbedImageData = {}

        data["url"] = url

        if proxy_url is not None:
            data["proxy_url"] = proxy_url

        if height is not None:
            data["height"] = height

        if width is not None:
            data["width"] = width

        data.update(extra)

        super().__init__(data)

class EmbedField(dict):
    """A class used to create an embed field for an embed."""
    def __init__(self, name: str, value: str, inline: bool = None, **extra) -> EmbedFieldData:
        """
        Creates an embed field.
        
        https://discord.com/developers/docs/resources/channel#embed-object-embed-field-structure
        """
        data: EmbedFieldData = {}

        data["name"] = name
        # TODO: Make this a goldy bot util function instead.
        data["value"] = utils.line_fix(value)

        if inline is not None:
            data["inline"] = inline

        data.update(extra)

        super().__init__(data)


class Embed(dict):
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
        title: str = None, 
        description: str = None, 
        fields: List[EmbedField] = None, 
        color: Colours | int = None, 
        colour: Colours | int = None, 
        footer: EmbedFooter = None,
        image: EmbedImage = None,
        thumbnail: EmbedImage = None,
        **extra
    ) -> EmbedData:
        """
        Creates a discord embed. 😋

        https://discord.com/developers/docs/resources/channel#embed-object
        """
        data: EmbedData = {}

        if title is not None:
            data["title"] = title

        if description is not None:
            data["description"] = utils.line_fix(description)

        if fields is not None:
            data["fields"] = []

            for field in fields:
                data["fields"].append(field)

        if color is None and colour is None:
            colour = Colours.INVISIBLE.value

        if color is not None:
            colour = color

        if colour is not None:
            if isinstance(colour, Colours):
                colour = colour.value
            
            data["color"] = colour

        if footer is not None:
            data["footer"] = footer

        if image is not None:
            data["image"] = image

        if thumbnail is not None:
            data["thumbnail"] = thumbnail

        data.update(extra)

        super().__init__(data)

    def format_title(self, **keys) -> None:
        "Just like the str.format() method but it formats the embed's title for you " \
        "so you can avoid the catastrophe at https://github.com/Goldy-Bot/Goldy-Bot-V5/issues/35."
        data: EmbedData = dict(self)

        data["title"] = data["title"].format(**keys)

        self.update(data)

    def format_description(self, **keys) -> None:
        "Just like the str.format() method but it formats the embed's description for you " \
        "so you can avoid the catastrophe at https://github.com/Goldy-Bot/Goldy-Bot-V5/issues/35."
        data: EmbedData = dict(self)

        data["description"] = data["description"].format(**keys)

        self.update(data)

    def format_fields(self, **keys) -> None:
        """
        Just like the str.format() method but it formats each of the embed's fields value.
        
        This was added because of https://github.com/Goldy-Bot/Goldy-Bot-V5/issues/35.
        """
        data: EmbedData = dict(self)

        for index, field in enumerate(data["fields"]):
            data["fields"][index]["value"] = field["value"].format(**keys)

        self.update(data)

    def copy(self) -> Embed:
        """Returns copy of embed."""
        return Embed(**copy.deepcopy(dict(self)))