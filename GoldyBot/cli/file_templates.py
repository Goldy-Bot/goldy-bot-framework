import os
from typing import List

from . import goldy_bot_logger

class FileTemplates():
    """Class that handles copying templates and stuff. This is some internal stuff don't worry much about it."""
    def __init__(self, file_template_paths:List[str]) -> None:
        self.file_template_paths = file_template_paths

    def copy_to(self, dest_path:str) -> None:
        dest_path = os.path.abspath(dest_path)

        for file_path in self.file_template_paths:
            file_name = os.path.split(file_path)[1]

            if file_name in os.listdir(dest_path):
                goldy_bot_logger.debug(f"'{file_name}' already exists in '{dest_path}', so we're skipping it.")
                continue

            template_file = open(file_path, mode="r")
            template_file.seek(0)
            file = open(dest_path + "/" + file_name, mode="w")
            file.write(template_file.read())
            file.close()

            goldy_bot_logger.debug(f"Created '{file_name}' file at '{dest_path}'!")
        
        return None