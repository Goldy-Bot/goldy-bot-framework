import logging as log
from devgoldyutils import Colours

# Logging module stuff
# -----------------------
class GoldyBotCustomFormatter(log.Formatter):
    format_string = "[%(levelname)s]\u001b[0m (%(name)s) - %(message)s"

    FORMATS = {
        log.DEBUG: Colours.PINK_GREY.value + format_string,
        log.INFO: Colours.CLAY.value + format_string,
        log.WARNING: Colours.YELLOW.value + format_string,
        log.ERROR: Colours.RED.value + format_string,
        log.CRITICAL: Colours.BOLD_RED.value + format_string
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = log.Formatter(log_fmt)
        return formatter.format(record)

class LoggerAdapter(log.LoggerAdapter):
    def __init__(self, logger:log.Logger, prefix:str):
        super().__init__(logger, {'prefix': prefix})

    def process(self, msg, kwargs):
        return f"\u001b[92m[{self.extra['prefix']}\u001b[92m]\u001b[0m {msg}", kwargs

# Method for adding custom handler to any logger object.
# -------------------------------------
def add_custom_handler(logger:log.Logger) -> log.Logger:
    stream_handler = log.StreamHandler()
    stream_handler.setLevel(log.DEBUG)
    stream_handler.setFormatter(GoldyBotCustomFormatter())

    logger.propagate = False
    logger.addHandler(stream_handler)

    return logger