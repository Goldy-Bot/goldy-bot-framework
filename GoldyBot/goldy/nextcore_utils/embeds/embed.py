from __future__ import annotations

from typing import List
from discord_typings import EmbedData, EmbedFieldData, EmbedImageData
from ..colours import Colours

class EmbedImage(dict):
    """A class used to add an image to a embed."""
    def __init__(self, url: str, proxy_url: str = None, height: int = None, width: int = None, **extra) -> EmbedImageData:
        """
        Creates an embed image or thumbnail. 😋
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
        Creates an embed field. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/resources/channel#embed-object-embed-field-structure
        """
        data: EmbedFieldData = {}

        data["name"] = name
        data["value"] = value

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
        title: str=None, 
        description: str=None, 
        fields: List[EmbedField] = None, 
        color: Colours | int = None, 
        colour: Colours | int = None, 
        image: EmbedImage = None,
        thumbnail: EmbedImage = None,
        **extra
    ) -> EmbedData:
        """
        Creates a discord embed. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/resources/channel#embed-object
        """
        data: EmbedData = {}

        if title is not None:
            data["title"] = title

        if description is not None:
            data["description"] = description

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

        if image is not None:
            data["image"] = image

        if thumbnail is not None:
            data["thumbnail"] = thumbnail

        data.update(extra)

        super().__init__(data)


    def copy(self) -> EmbedData:
        return super().copy()

