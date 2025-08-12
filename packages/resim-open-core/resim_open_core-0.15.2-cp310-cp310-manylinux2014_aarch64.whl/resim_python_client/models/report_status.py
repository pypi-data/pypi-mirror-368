from enum import Enum

class ReportStatus(str, Enum):
    ERROR = "ERROR"
    RUNNING = "RUNNING"
    SUBMITTED = "SUBMITTED"
    SUCCEEDED = "SUCCEEDED"

    def __str__(self) -> str:
        return str(self.value)
