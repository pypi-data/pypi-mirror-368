from enum import Enum

class CompareBatchesStatusFilter(str, Enum):
    BOTH_FAILING = "BOTH_FAILING"
    BOTH_PASSING = "BOTH_PASSING"
    ONE_FAILING = "ONE_FAILING"

    def __str__(self) -> str:
        return str(self.value)
