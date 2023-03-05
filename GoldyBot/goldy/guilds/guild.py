from typing import List, Dict
from dataclasses import dataclass, field

@dataclass
class Guild:
    """A dataclass representing a Goldy Bot guild."""
    id:str
    code_name:str

    config_dict:dict = field(repr=False)

    prefix:str = field(init=False)
    roles:Dict[str, str] = field(init=False)
    channels:Dict[str, str] = field(init=False)

    allowed_extensions:List[str] = field(init=False)
    disallowed_extensions:List[str] = field(init=False)
    hidden_extensions:List[str] = field(init=False)

    def __post_init__(self):
        self.prefix = self.config_dict["prefix"]
        self.roles = self.config_dict["roles"]
        self.channels = self.config_dict["channels"]
        self.allowed_extensions = self.config_dict["allowed_extensions"]
        self.disallowed_extensions = self.config_dict["disallowed_extensions"]
        self.hidden_extensions = self.config_dict["hidden_extensions"]
