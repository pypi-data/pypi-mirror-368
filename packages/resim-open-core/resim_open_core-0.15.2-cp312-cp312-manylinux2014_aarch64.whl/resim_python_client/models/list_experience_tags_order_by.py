from enum import Enum

class ListExperienceTagsOrderBy(str, Enum):
    ID = "id"
    RANK = "rank"
    TIMESTAMP = "timestamp"

    def __str__(self) -> str:
        return str(self.value)
