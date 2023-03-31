from typing import List
from discord_typings import EmbedData, EmbedFieldData

class EmbedField(dict):
    """A class used to create an embed field for an embed."""
    def __init__(self, name:str, value:str, inline:bool=None, **extra):
        """
        Creates an embed field. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/resources/channel#embed-object-embed-field-structure
        """
        self.data: EmbedFieldData = {}

        if name is not None:
            self.data["name"] = name

        if value is not None:
            self.data["value"] = value

        self.data.update(extra)

        super().__init__(self.data)
        

class Embed(dict):
    """A class used to create a discord embed."""
    def __init__(self, title:str=None, description:str=None, fields:List[EmbedField]=None, **extra) -> None:
        """
        Creates a discord embed. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/resources/channel#embed-object
        """
        self.data: EmbedData = {}

        if title is not None:
            self.data["title"] = title

        if description is not None:
            self.data["description"] = description

        if fields is not None:
            self.data["fields"] = []

            for field in fields:
                self.data["fields"].append(field)

        self.data.update(extra)

        super().__init__(self.data)

