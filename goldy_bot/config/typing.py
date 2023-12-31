from typing import TypedDict, Literal, List

__all__ = (
    "ConfigData",
    "VersionT"
)

BrandingData = TypedDict(
    "BrandingData", {
        "name": str,
        "emoticon": str
    }
)

ExtensionsLoadData = TypedDict(
    "ExtensionsLoadData", {
        "directory": str,
        "raise_on_error": bool
    }
)

ExtensionsData = TypedDict(
    "ExtensionsData", {
        "repos": List[str],
        "include": List[str],
        "ignore": List[str],
        "load": ExtensionsLoadData
    }
)

DevelopmentData = TypedDict(
    "DevelopmentData", {
        "test_guild_id": str,
        "developer_id": str
    }
)

VersionT = Literal[2]

class ConfigData(TypedDict):
    version: VersionT
    branding: BrandingData
    extensions: ExtensionsData
    development: DevelopmentData