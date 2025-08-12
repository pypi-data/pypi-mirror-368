from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="JobMetricsStatusCounts")


@_attrs_define
class JobMetricsStatusCounts:
    """ 
        Attributes:
            fail_block (int):
            fail_warn (int):
            no_status_reported (int):
            not_applicable (int):
            passed (int):
            raw (int):
     """

    fail_block: int
    fail_warn: int
    no_status_reported: int
    not_applicable: int
    passed: int
    raw: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        fail_block = self.fail_block

        fail_warn = self.fail_warn

        no_status_reported = self.no_status_reported

        not_applicable = self.not_applicable

        passed = self.passed

        raw = self.raw


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "failBlock": fail_block,
            "failWarn": fail_warn,
            "noStatusReported": no_status_reported,
            "notApplicable": not_applicable,
            "passed": passed,
            "raw": raw,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        fail_block = d.pop("failBlock")

        fail_warn = d.pop("failWarn")

        no_status_reported = d.pop("noStatusReported")

        not_applicable = d.pop("notApplicable")

        passed = d.pop("passed")

        raw = d.pop("raw")

        job_metrics_status_counts = cls(
            fail_block=fail_block,
            fail_warn=fail_warn,
            no_status_reported=no_status_reported,
            not_applicable=not_applicable,
            passed=passed,
            raw=raw,
        )


        job_metrics_status_counts.additional_properties = d
        return job_metrics_status_counts

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
