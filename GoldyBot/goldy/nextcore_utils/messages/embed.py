from discord_typings import EmbedData

class Embed(dict):
    """A class used to create a discord embed."""
    def __init__(self, title:str=None, description:str=None, **extra) -> None:
        """
        Creates a discord embed. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/resources/channel#embed-object
        """
        self.payload: EmbedData = {}

        if title is not None:
            self.payload["title"] = title

        if title is not None:
            self.payload["description"] = description

        self.payload.update(extra)

        super().__init__(self.payload)