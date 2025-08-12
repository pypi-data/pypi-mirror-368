from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
import datetime
from typing import cast
from typing import Dict
from dateutil.parser import isoparse

if TYPE_CHECKING:
  from ..models.custom_metric import CustomMetric





T = TypeVar("T", bound="TestSuiteBatchSummaryJobResults")


@_attrs_define
class TestSuiteBatchSummaryJobResults:
    """ 
        Attributes:
            batch_creation_timestamp (datetime.datetime):
            batch_id (str):
            blocker (int):
            build_creation_timestamp (datetime.datetime):
            build_id (str):
            cancelled (int):
            error (int):
            metrics (List['CustomMetric']):
            passed (int):
            queued (int):
            running (int):
            total (int):
            warning (int):
     """

    batch_creation_timestamp: datetime.datetime
    batch_id: str
    blocker: int
    build_creation_timestamp: datetime.datetime
    build_id: str
    cancelled: int
    error: int
    metrics: List['CustomMetric']
    passed: int
    queued: int
    running: int
    total: int
    warning: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.custom_metric import CustomMetric
        batch_creation_timestamp = self.batch_creation_timestamp.isoformat()

        batch_id = self.batch_id

        blocker = self.blocker

        build_creation_timestamp = self.build_creation_timestamp.isoformat()

        build_id = self.build_id

        cancelled = self.cancelled

        error = self.error

        metrics = []
        for metrics_item_data in self.metrics:
            metrics_item = metrics_item_data.to_dict()
            metrics.append(metrics_item)



        passed = self.passed

        queued = self.queued

        running = self.running

        total = self.total

        warning = self.warning


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "batchCreationTimestamp": batch_creation_timestamp,
            "batchID": batch_id,
            "blocker": blocker,
            "buildCreationTimestamp": build_creation_timestamp,
            "buildID": build_id,
            "cancelled": cancelled,
            "error": error,
            "metrics": metrics,
            "passed": passed,
            "queued": queued,
            "running": running,
            "total": total,
            "warning": warning,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.custom_metric import CustomMetric
        d = src_dict.copy()
        batch_creation_timestamp = isoparse(d.pop("batchCreationTimestamp"))




        batch_id = d.pop("batchID")

        blocker = d.pop("blocker")

        build_creation_timestamp = isoparse(d.pop("buildCreationTimestamp"))




        build_id = d.pop("buildID")

        cancelled = d.pop("cancelled")

        error = d.pop("error")

        metrics = []
        _metrics = d.pop("metrics")
        for metrics_item_data in (_metrics):
            metrics_item = CustomMetric.from_dict(metrics_item_data)



            metrics.append(metrics_item)


        passed = d.pop("passed")

        queued = d.pop("queued")

        running = d.pop("running")

        total = d.pop("total")

        warning = d.pop("warning")

        test_suite_batch_summary_job_results = cls(
            batch_creation_timestamp=batch_creation_timestamp,
            batch_id=batch_id,
            blocker=blocker,
            build_creation_timestamp=build_creation_timestamp,
            build_id=build_id,
            cancelled=cancelled,
            error=error,
            metrics=metrics,
            passed=passed,
            queued=queued,
            running=running,
            total=total,
            warning=warning,
        )


        test_suite_batch_summary_job_results.additional_properties = d
        return test_suite_batch_summary_job_results

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
