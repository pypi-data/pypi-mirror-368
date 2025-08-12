from enum import Enum

class MetricStatus(str, Enum):
    FAIL_BLOCK = "FAIL_BLOCK"
    FAIL_WARN = "FAIL_WARN"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NO_STATUS_REPORTED = "NO_STATUS_REPORTED"
    PASSED = "PASSED"
    RAW = "RAW"

    def __str__(self) -> str:
        return str(self.value)
