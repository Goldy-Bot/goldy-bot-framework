from __future__ import annotations
from typing import List

from ... import info
from dataclasses import dataclass, field

@dataclass
class ExtensionAuthor:
    name: str
    email: str

@dataclass
class ExtensionMetadata:
    data: dict = field(repr=False)

    description: str = field(init=False)
    authors: List[ExtensionAuthor] = field(init=False)
    dependencies: List[str] = field(init=False)
    url: str = field(init=False)
    version: str = field(init=False)

    def __post_init__(self):
        project: dict = self.data.get("project")
        project_urls: dict = project.get("urls")

        self.description = project.get("description")
        self.authors = [ExtensionAuthor(x["name"], x["email"]) for x in project.get("authors")]
        self.dependencies = project.get("dependencies")
        self.url = project_urls.get("GitHub") if project_urls.get("GitHub") is not None else project_urls.get("github", info.GITHUB_REPO)
        self.version = project.get("version")