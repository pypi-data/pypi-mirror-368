from enum import Enum

class JobStatus(str, Enum):
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"
    EXPERIENCE_RUNNING = "EXPERIENCE_RUNNING"
    METRICS_QUEUED = "METRICS_QUEUED"
    METRICS_RUNNING = "METRICS_RUNNING"
    SUBMITTED = "SUBMITTED"
    SUCCEEDED = "SUCCEEDED"

    def __str__(self) -> str:
        return str(self.value)
