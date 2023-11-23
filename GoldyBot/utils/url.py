from urllib.parse import ParseResult

__all__ = ("get_github_file",)

def get_github_file(phrased_url: ParseResult, tag: str, file_name: str) -> str:
    return "https://raw.githubusercontent.com" + phrased_url.path + f"/{tag}/{file_name}"