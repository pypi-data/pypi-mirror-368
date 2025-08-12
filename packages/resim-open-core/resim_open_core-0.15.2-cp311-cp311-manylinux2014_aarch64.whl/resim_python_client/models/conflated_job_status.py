from enum import Enum

class ConflatedJobStatus(str, Enum):
    BLOCKER = "BLOCKER"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"
    PASSED = "PASSED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WARNING = "WARNING"

    def __str__(self) -> str:
        return str(self.value)
