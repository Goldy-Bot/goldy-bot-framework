# Version info
# --------------
VER = 5.0
"""Just the version number as an integer. E.g ``5.0``."""
STAGE = ("dev", 7)

VERSION = f"{VER}{STAGE[0]}{STAGE[1]}"
"""Goldy Bot version string. E.g ``5.0alpha8``."""

DISPLAY_NAME = f"Goldy Bot (v{VERSION})"
"""Display name of goldy bot with it's version, like e.g ``Goldy Bot (v5.0alpha8)``."""

GITHUB_REPO = "https://github.com/Goldy-Bot/Goldy-Bot-V5"

COPYRIGHT = "Copyright (C) 2023 - Goldy"

__version__ = VERSION