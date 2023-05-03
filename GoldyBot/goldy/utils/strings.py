import re

def line_fix(string: str) -> str:
    """Fixes this -> https://github.com/Goldy-Bot/Goldy-Bot-V5/issues/37"""
    return "".join([re.sub(' +', ' ', line)[1:] + "\n" for line in string.splitlines()])