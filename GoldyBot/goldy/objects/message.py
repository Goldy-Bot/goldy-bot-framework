from dataclasses import dataclass, field

from discord_typings import MessageData

@dataclass
class Message:
    data:MessageData = field(repr=False)

    # TODO: Add more fields here to data inside the data dict.