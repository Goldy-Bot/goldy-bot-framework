import re

def line_fix(string: str) -> str:
    """Fixes this -> https://github.com/Goldy-Bot/Goldy-Bot-V5/issues/37"""
    return "".join(
        [re.sub(' +', ' ', line)[1 if string[0] == "\n" else 0:] + "\n" for line in string.splitlines()]
    )