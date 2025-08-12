from enum import Enum

class BatchType(str, Enum):
    DEBUG_EXPERIENCE = "DEBUG_EXPERIENCE"
    NORMAL = "NORMAL"

    def __str__(self) -> str:
        return str(self.value)
