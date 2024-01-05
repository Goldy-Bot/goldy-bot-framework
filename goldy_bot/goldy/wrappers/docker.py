import os

__all__ = (
    "Docker",
)

class Docker():
    def __init__(self) -> None:
        super().__init__()

    @property
    def in_docker(self) -> bool:
        """Returns True it goldy bot is running in a docker container."""
        if "DOCKER" in os.environ:
            return True

        return False