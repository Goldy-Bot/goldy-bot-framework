import pathlib

class Paths:
    """Class containing important paths like template files and stuff."""
    
    GOLDY_BOT_ROOT = pathlib.Path(__file__).parent.resolve()

    # File templates.
    # -----------------
    ASSETS = str(GOLDY_BOT_ROOT) + "/assets"

    TOKEN_ENV_TEMPLATE = ASSETS + "/token.env"

    GOLDY_JSON_TEMPLATE = ASSETS + "/goldy.json"

    RUN_SCRIPT_TEMPLATE = ASSETS + "/run.py"

    # Internal Extensions
    # ---------------------
    INTERNAL_EXTENSIONS = str(GOLDY_BOT_ROOT) + "/internal_extensions"