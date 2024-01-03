from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Dict

    from ..goldy import Goldy
    from ...typings import RepoData, ExtensionRepoData

import os
import sys
import toml
import requests
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from devgoldyutils import shorter_path

__all__ = (
    "RepoWrapper",
)

class RepoWrapper():
    def __init__(self) -> None:
        self.__repo_data: Tuple[List[str], Dict[str, ExtensionRepoData]] = None

        super().__init__()

    def pull_extension(self: Goldy | RepoWrapper, extension_name: str, destination_folder: Path, repos: Optional[List[str]] = None) -> None:
        """
        Pulls down the extension that you specified from the official goldy bot repo into the destination folder if it doesn't already exist.
        """
        extension_name = extension_name.lower()

        if repos is None:
            repos = self.config.repos

        if not destination_folder.exists():
            destination_folder.mkdir()
            self.logger.debug(
                f"Created destination folder '{destination_folder}' as it didn't exist for pulling."
            )

        self.logger.info(f"Pulling extension '{extension_name}' to '{destination_folder}'...")

        repo_extensions = self.__get_repo_data(repos)
        extension_path = destination_folder.joinpath(extension_name)

        if extension_name not in repo_extensions:
            self.logger.error(f"Could not find the extension '{extension_name}' in these repositories!")
            return False

        self.logger.debug(f"Found '{extension_name}' extension in repo.")

        if extension_path.exists():
            self.logger.debug(f"'{extension_name}' already exists so we will not git clone it.") 
            # TODO: Should we have this git pull new commits instead?
            return True

        self.logger.info(f"Adding '{extension_name}' extension as git sub module...")
        git_url = repo_extensions[extension_name]["git_url"]

        subprocess.check_call(
            ["git", "submodule", "add", "-f", git_url, str(extension_path)]
        )

        return True

    def _remove_unwanted_extensions(self: Goldy, extension_path: Path, included_extensions: List[str]) -> None:
        """Removes extensions in the path that are not present in the included list."""
        self.logger.info("Removing unwanted extensions...")

        for path in extension_path.iterdir():
            shortened_path = shorter_path(path)

            if path.is_file() or path.name in included_extensions:
                self.logger.debug(f"'{shortened_path}' is safe from removal.")
                continue

            is_submodule = self.__is_extension_git_submodule(path.name)

            if not is_submodule:
                self.logger.debug(f"'{shortened_path}' is safe from removal as it is not a valid git submodule.")
                continue

            self.logger.warning(
                f"Removing the extension at '{shortened_path}' as it's not included."
            )

            subprocess.call(["git", "rm", f"{path}", "-f"])

            self.logger.info(f"The extension at '{shortened_path}' was removed.")

    def _git_setup(self: Goldy) -> None:
        """Makes sure git is ready for goldy bot operations."""
        if ".git" not in os.listdir("."):
            self.logger.debug("Root directory is not a git repository so I'm making it one...")
            os.system("git init")

        if ".gitmodules" not in os.listdir("."):
            self.logger.debug("No '.gitmodules' file in root so I'm creating one...")
            open(".gitmodules", "w").close()

        if ".gitattributes" not in os.listdir("."):
            self.logger.debug("No '.gitattributes' file in root so I'm creating one...")
            with open(".gitattributes", "w") as file:
                file.write("# Auto detect text files and perform LF normalization\n* text=auto")

        if self.in_docker:
            self.logger.debug("Setting root path to git's safe directory as you are running under docker...")
            subprocess.run(
                ["git", "config", "--global", "--add", "safe.directory", "/app/goldy"]
            )

    def __get_repo_data(self: Goldy | RepoData, repos: List[str]) -> Dict[str, ExtensionRepoData]:
        """Method to retrieve data from goldy bot repositories. Supports GitHub urls and caches data."""
        repos.reverse() # I reverse it so whatever repo you add after 
        # the main repo the extensions there are sure to override the main repo.

        if self.__repo_data is None or not repos == self.__repo_data[0]:
            merged_extensions: Dict[str, ExtensionRepoData] = {}

            for repo_url in repos:
                phrased_url = urlparse(repo_url)

                if "github.com" in phrased_url.netloc:
                    repo_url = "https://raw.githubusercontent.com" + phrased_url.path + "/main/repo.toml"

                self.logger.debug(f"Making request to repo at '{repo_url}'...")
                r = requests.get(repo_url)

                if r.ok:
                    repo_data: RepoData = toml.loads(r.text)
                    repo_data_copy = repo_data.copy()

                    # I do this because I allow the repo.toml file to be flexible by allowing 
                    # users to just enter the git url as the definite value for extensions instead of the normal dict.
                    for extension in repo_data["extensions"]:
                        extension_url_maybe = repo_data["extensions"][extension]

                        if isinstance(extension_url_maybe, str):
                            repo_data_copy["extensions"][extension] = {"git_url": extension_url_maybe}

                    merged_extensions.update(repo_data_copy["extensions"])
                else:
                    self.logger.error(
                        f"Failed to get this repo! Extensions in that repo will not be pulled! \nResponse: {r}"
                    )

            self.__repo_data = (repos, merged_extensions)

        return self.__repo_data[1]

    def __is_extension_git_submodule(self: Goldy | RepoWrapper, extension_name: str) -> bool:
        """Stats whether a git submodule for this extension exists."""
        submodule_extension_paths = []

        try:
            git_submodule_output = subprocess.check_output(["git", "submodule"], encoding = "utf+8")
            submodule_extension_paths = [x[1:].split(" ")[1] for x in git_submodule_output.splitlines()]
        except subprocess.CalledProcessError as e:

            if e.returncode == 128:
                self.logger.warning(
                    "Git detects that .gitsubmodules has been tampered with. " \
                        "Please do not mess with this file as it will break the management of goldy bot extensions."
                )
                return False

            raise e

        if sys.platform == "win32": # IDK WHY THE FUCK THAT COMMAND ABOVE MAKES ME LOOSE COLOUR ON WINDOWS!!! AUGHHHHHHHHHHHH!
            os.system("color")

        for submodule_path in submodule_extension_paths:
            submodule_name = submodule_path.split("/")[-1]

            if extension_name == submodule_name:
                return True

        return False