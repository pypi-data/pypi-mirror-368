from enum import Enum

class TriggeredVia(str, Enum):
    GITHUB = "GITHUB"
    GITLAB = "GITLAB"
    LOCAL = "LOCAL"
    WEBAPP = "WEBAPP"

    def __str__(self) -> str:
        return str(self.value)
