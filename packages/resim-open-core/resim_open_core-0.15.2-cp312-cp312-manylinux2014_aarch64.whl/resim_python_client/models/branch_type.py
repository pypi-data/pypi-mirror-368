from enum import Enum

class BranchType(str, Enum):
    CHANGE_REQUEST = "CHANGE_REQUEST"
    MAIN = "MAIN"
    RELEASE = "RELEASE"

    def __str__(self) -> str:
        return str(self.value)
