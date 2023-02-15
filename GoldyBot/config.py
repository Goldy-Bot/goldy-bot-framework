import json
from devgoldyutils import Colours

from . import goldy_bot_logger, LoggerAdapter

class Config():
    """The base config class that all json configuration classes should inherit from."""
    def __init__(self, json_path:str):
        self.json_path = json_path
        self.logger = LoggerAdapter(goldy_bot_logger, prefix="Config")

        self.logger.debug(f"Opening config file at '{self.json_path}'...")
        self.file = open(
            self.json_path, 
            "r+", 
            encoding='utf-8'
        )

        self.logger.debug("Phrasing json in config to dict...")
        self.json_data:dict = json.loads(self.file.read())
        self.logger.debug(Colours.GREEN.apply_to_string("Done!"))