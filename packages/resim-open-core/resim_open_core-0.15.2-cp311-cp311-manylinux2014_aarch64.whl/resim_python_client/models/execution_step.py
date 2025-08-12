from enum import Enum

class ExecutionStep(str, Enum):
    BATCH_METRICS = "BATCH_METRICS"
    EXPERIENCE = "EXPERIENCE"
    METRICS = "METRICS"
    REPORT = "REPORT"

    def __str__(self) -> str:
        return str(self.value)
