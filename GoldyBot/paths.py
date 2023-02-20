import pathlib

class Paths:
    """Class containing important paths like template files and stuff."""
    
    GOLDY_BOT_ROOT = pathlib.Path(__file__).parent.resolve()

    # File templates.
    # -----------------
    FILE_TEMPLATES = str(GOLDY_BOT_ROOT) + "/file_templates"

    TOKEN_ENV_TEMPLATE = FILE_TEMPLATES + "/token.env"

    GOLDY_JSON_TEMPLATE = FILE_TEMPLATES + "/goldy.json"

    RUN_SCRIPT_TEMPLATE = FILE_TEMPLATES + "/run.py"

    # Internal Extensions
    # ---------------------
    INTERNAL_EXTENSIONS = str(GOLDY_BOT_ROOT) + "/internal_extensions"