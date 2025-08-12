from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="BatchJobStatusCounts")


@_attrs_define
class BatchJobStatusCounts:
    """ 
        Attributes:
            cancelled (int):
            error (int):
            metrics_queued (int):
            metrics_running (int):
            running (int):
            submitted (int):
            succeeded (int):
     """

    cancelled: int
    error: int
    metrics_queued: int
    metrics_running: int
    running: int
    submitted: int
    succeeded: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        cancelled = self.cancelled

        error = self.error

        metrics_queued = self.metrics_queued

        metrics_running = self.metrics_running

        running = self.running

        submitted = self.submitted

        succeeded = self.succeeded


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "cancelled": cancelled,
            "error": error,
            "metricsQueued": metrics_queued,
            "metricsRunning": metrics_running,
            "running": running,
            "submitted": submitted,
            "succeeded": succeeded,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cancelled = d.pop("cancelled")

        error = d.pop("error")

        metrics_queued = d.pop("metricsQueued")

        metrics_running = d.pop("metricsRunning")

        running = d.pop("running")

        submitted = d.pop("submitted")

        succeeded = d.pop("succeeded")

        batch_job_status_counts = cls(
            cancelled=cancelled,
            error=error,
            metrics_queued=metrics_queued,
            metrics_running=metrics_running,
            running=running,
            submitted=submitted,
            succeeded=succeeded,
        )


        batch_job_status_counts.additional_properties = d
        return batch_job_status_counts

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
