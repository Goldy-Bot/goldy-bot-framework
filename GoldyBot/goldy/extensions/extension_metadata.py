from __future__ import annotations
from typing import List

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
    version: str = field(init=False)

    def __post_init__(self):
        project: dict = self.data.get("project")

        self.description = project.get("description")
        self.authors = [ExtensionAuthor(x["name"], x["email"]) for x in project.get("authors")]
        self.dependencies = project.get("dependencies")
        self.version = project.get("version")