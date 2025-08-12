from enum import Enum

class MetricType(str, Enum):
    COMPOSITE = "COMPOSITE"
    SCALAR = "SCALAR"

    def __str__(self) -> str:
        return str(self.value)
