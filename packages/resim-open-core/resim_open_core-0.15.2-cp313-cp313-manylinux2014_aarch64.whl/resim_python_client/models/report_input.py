from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

import datetime
from dateutil.parser import isoparse
from typing import cast, Union
from typing import cast
from typing import cast, List
from ..types import UNSET, Unset
from typing import Union
from ..models.triggered_via import TriggeredVia






T = TypeVar("T", bound="ReportInput")


@_attrs_define
class ReportInput:
    """ 
        Attributes:
            branch_id (str):
            metrics_build_id (str):
            start_timestamp (datetime.datetime):
            test_suite_id (str):
            associated_account (Union[Unset, str]):
            end_timestamp (Union[Unset, datetime.datetime]):
            metrics_set_name (Union[None, Unset, str]):
            name (Union[Unset, str]):
            pool_labels (Union[Unset, List[str]]):
            respect_revision_boundary (Union[Unset, bool]):
            test_suite_revision (Union[Unset, int]):
            triggered_via (Union[Unset, TriggeredVia]):
     """

    branch_id: str
    metrics_build_id: str
    start_timestamp: datetime.datetime
    test_suite_id: str
    associated_account: Union[Unset, str] = UNSET
    end_timestamp: Union[Unset, datetime.datetime] = UNSET
    metrics_set_name: Union[None, Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    pool_labels: Union[Unset, List[str]] = UNSET
    respect_revision_boundary: Union[Unset, bool] = UNSET
    test_suite_revision: Union[Unset, int] = UNSET
    triggered_via: Union[Unset, TriggeredVia] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        branch_id = self.branch_id

        metrics_build_id = self.metrics_build_id

        start_timestamp = self.start_timestamp.isoformat()

        test_suite_id = self.test_suite_id

        associated_account = self.associated_account

        end_timestamp: Union[Unset, str] = UNSET
        if not isinstance(self.end_timestamp, Unset):
            end_timestamp = self.end_timestamp.isoformat()

        metrics_set_name: Union[None, Unset, str]
        if isinstance(self.metrics_set_name, Unset):
            metrics_set_name = UNSET
        else:
            metrics_set_name = self.metrics_set_name

        name = self.name

        pool_labels: Union[Unset, List[str]] = UNSET
        if not isinstance(self.pool_labels, Unset):
            pool_labels = self.pool_labels



        respect_revision_boundary = self.respect_revision_boundary

        test_suite_revision = self.test_suite_revision

        triggered_via: Union[Unset, str] = UNSET
        if not isinstance(self.triggered_via, Unset):
            triggered_via = self.triggered_via.value



        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "branchID": branch_id,
            "metricsBuildID": metrics_build_id,
            "startTimestamp": start_timestamp,
            "testSuiteID": test_suite_id,
        })
        if associated_account is not UNSET:
            field_dict["associatedAccount"] = associated_account
        if end_timestamp is not UNSET:
            field_dict["endTimestamp"] = end_timestamp
        if metrics_set_name is not UNSET:
            field_dict["metricsSetName"] = metrics_set_name
        if name is not UNSET:
            field_dict["name"] = name
        if pool_labels is not UNSET:
            field_dict["poolLabels"] = pool_labels
        if respect_revision_boundary is not UNSET:
            field_dict["respectRevisionBoundary"] = respect_revision_boundary
        if test_suite_revision is not UNSET:
            field_dict["testSuiteRevision"] = test_suite_revision
        if triggered_via is not UNSET:
            field_dict["triggeredVia"] = triggered_via

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        branch_id = d.pop("branchID")

        metrics_build_id = d.pop("metricsBuildID")

        start_timestamp = isoparse(d.pop("startTimestamp"))




        test_suite_id = d.pop("testSuiteID")

        associated_account = d.pop("associatedAccount", UNSET)

        _end_timestamp = d.pop("endTimestamp", UNSET)
        end_timestamp: Union[Unset, datetime.datetime]
        if isinstance(_end_timestamp,  Unset):
            end_timestamp = UNSET
        else:
            end_timestamp = isoparse(_end_timestamp)




        def _parse_metrics_set_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        metrics_set_name = _parse_metrics_set_name(d.pop("metricsSetName", UNSET))


        name = d.pop("name", UNSET)

        pool_labels = cast(List[str], d.pop("poolLabels", UNSET))


        respect_revision_boundary = d.pop("respectRevisionBoundary", UNSET)

        test_suite_revision = d.pop("testSuiteRevision", UNSET)

        _triggered_via = d.pop("triggeredVia", UNSET)
        triggered_via: Union[Unset, TriggeredVia]
        if isinstance(_triggered_via,  Unset):
            triggered_via = UNSET
        else:
            triggered_via = TriggeredVia(_triggered_via)




        report_input = cls(
            branch_id=branch_id,
            metrics_build_id=metrics_build_id,
            start_timestamp=start_timestamp,
            test_suite_id=test_suite_id,
            associated_account=associated_account,
            end_timestamp=end_timestamp,
            metrics_set_name=metrics_set_name,
            name=name,
            pool_labels=pool_labels,
            respect_revision_boundary=respect_revision_boundary,
            test_suite_revision=test_suite_revision,
            triggered_via=triggered_via,
        )


        report_input.additional_properties = d
        return report_input

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
