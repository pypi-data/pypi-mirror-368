from enum import Enum

class ParameterSweepStatus(str, Enum):
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"
    RUNNING = "RUNNING"
    SUBMITTED = "SUBMITTED"
    SUCCEEDED = "SUCCEEDED"

    def __str__(self) -> str:
        return str(self.value)
