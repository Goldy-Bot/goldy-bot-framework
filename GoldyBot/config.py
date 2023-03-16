from devgoldyutils.file_configs import JSONConfig

from . import goldy_bot_logger

# I moved this to my utils library: 
# https://github.com/THEGOLDENPRO/devgoldyutils/blob/master/devgoldyutils/file_configs.py#L6

class Config(JSONConfig):
    """The base config class that all json configuration classes should inherit from."""
    def __init__(self, json_path:str):
        super().__init__(json_path, goldy_bot_logger)