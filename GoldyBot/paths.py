import pathlib

class Paths:
    """Class containing important paths."""
    
    GOLDY_BOT_ROOT = pathlib.Path(__file__).parent.resolve()

    # File templates.
    # -----------------
    FILE_TEMPLATES = str(GOLDY_BOT_ROOT) + "/file_templates"

    TOKEN_ENV = FILE_TEMPLATES + "/token.env"