from enum import Enum

class LogType(str, Enum):
    ARCHIVE_LOG = "ARCHIVE_LOG"
    CONTAINER_LOG = "CONTAINER_LOG"
    EMISSIONS_LOG = "EMISSIONS_LOG"
    ERROR_LOG = "ERROR_LOG"
    EXECUTION_LOG = "EXECUTION_LOG"
    FOXGLOVE_MCAP_LOG = "FOXGLOVE_MCAP_LOG"
    MCAP_LOG = "MCAP_LOG"
    METRICS_OUTPUT_LOG = "METRICS_OUTPUT_LOG"
    MP4_LOG = "MP4_LOG"
    OTHER_LOG = "OTHER_LOG"
    RERUN_IO_LOG = "RERUN_IO_LOG"
    SERVICE_LOG = "SERVICE_LOG"

    def __str__(self) -> str:
        return str(self.value)
