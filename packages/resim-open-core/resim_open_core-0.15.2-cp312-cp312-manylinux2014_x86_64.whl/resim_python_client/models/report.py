from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
from typing import Union
from ..models.triggered_via import TriggeredVia
from ..models.metric_status import MetricStatus
import datetime
from typing import cast
from ..types import UNSET, Unset
from typing import Dict
from typing import cast, Union
from ..models.report_status import ReportStatus
from dateutil.parser import isoparse

if TYPE_CHECKING:
  from ..models.report_status_history_type import ReportStatusHistoryType





T = TypeVar("T", bound="Report")


@_attrs_define
class Report:
    """ 
        Attributes:
            associated_account (str):
            branch_id (str):
            creation_timestamp (datetime.datetime):
            end_timestamp (datetime.datetime):
            last_updated_timestamp (datetime.datetime):
            metrics_build_id (str):
            metrics_set_name (Union[None, str]):
            metrics_status (MetricStatus):
            name (str):
            org_id (str):
            output_location (str):
            project_id (str):
            report_id (str):
            respect_revision_boundary (bool):
            start_timestamp (datetime.datetime):
            status (ReportStatus):
            status_history (List['ReportStatusHistoryType']):
            test_suite_id (str):
            test_suite_revision (int):
            user_id (str):
            triggered_via (Union[Unset, TriggeredVia]):
     """

    associated_account: str
    branch_id: str
    creation_timestamp: datetime.datetime
    end_timestamp: datetime.datetime
    last_updated_timestamp: datetime.datetime
    metrics_build_id: str
    metrics_set_name: Union[None, str]
    metrics_status: MetricStatus
    name: str
    org_id: str
    output_location: str
    project_id: str
    report_id: str
    respect_revision_boundary: bool
    start_timestamp: datetime.datetime
    status: ReportStatus
    status_history: List['ReportStatusHistoryType']
    test_suite_id: str
    test_suite_revision: int
    user_id: str
    triggered_via: Union[Unset, TriggeredVia] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.report_status_history_type import ReportStatusHistoryType
        associated_account = self.associated_account

        branch_id = self.branch_id

        creation_timestamp = self.creation_timestamp.isoformat()

        end_timestamp = self.end_timestamp.isoformat()

        last_updated_timestamp = self.last_updated_timestamp.isoformat()

        metrics_build_id = self.metrics_build_id

        metrics_set_name: Union[None, str]
        metrics_set_name = self.metrics_set_name

        metrics_status = self.metrics_status.value

        name = self.name

        org_id = self.org_id

        output_location = self.output_location

        project_id = self.project_id

        report_id = self.report_id

        respect_revision_boundary = self.respect_revision_boundary

        start_timestamp = self.start_timestamp.isoformat()

        status = self.status.value

        status_history = []
        for componentsschemasreport_status_history_item_data in self.status_history:
            componentsschemasreport_status_history_item = componentsschemasreport_status_history_item_data.to_dict()
            status_history.append(componentsschemasreport_status_history_item)



        test_suite_id = self.test_suite_id

        test_suite_revision = self.test_suite_revision

        user_id = self.user_id

        triggered_via: Union[Unset, str] = UNSET
        if not isinstance(self.triggered_via, Unset):
            triggered_via = self.triggered_via.value



        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "associatedAccount": associated_account,
            "branchID": branch_id,
            "creationTimestamp": creation_timestamp,
            "endTimestamp": end_timestamp,
            "lastUpdatedTimestamp": last_updated_timestamp,
            "metricsBuildID": metrics_build_id,
            "metricsSetName": metrics_set_name,
            "metricsStatus": metrics_status,
            "name": name,
            "orgID": org_id,
            "outputLocation": output_location,
            "projectID": project_id,
            "reportID": report_id,
            "respectRevisionBoundary": respect_revision_boundary,
            "startTimestamp": start_timestamp,
            "status": status,
            "statusHistory": status_history,
            "testSuiteID": test_suite_id,
            "testSuiteRevision": test_suite_revision,
            "userID": user_id,
        })
        if triggered_via is not UNSET:
            field_dict["triggeredVia"] = triggered_via

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.report_status_history_type import ReportStatusHistoryType
        d = src_dict.copy()
        associated_account = d.pop("associatedAccount")

        branch_id = d.pop("branchID")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        end_timestamp = isoparse(d.pop("endTimestamp"))




        last_updated_timestamp = isoparse(d.pop("lastUpdatedTimestamp"))




        metrics_build_id = d.pop("metricsBuildID")

        def _parse_metrics_set_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        metrics_set_name = _parse_metrics_set_name(d.pop("metricsSetName"))


        metrics_status = MetricStatus(d.pop("metricsStatus"))




        name = d.pop("name")

        org_id = d.pop("orgID")

        output_location = d.pop("outputLocation")

        project_id = d.pop("projectID")

        report_id = d.pop("reportID")

        respect_revision_boundary = d.pop("respectRevisionBoundary")

        start_timestamp = isoparse(d.pop("startTimestamp"))




        status = ReportStatus(d.pop("status"))




        status_history = []
        _status_history = d.pop("statusHistory")
        for componentsschemasreport_status_history_item_data in (_status_history):
            componentsschemasreport_status_history_item = ReportStatusHistoryType.from_dict(componentsschemasreport_status_history_item_data)



            status_history.append(componentsschemasreport_status_history_item)


        test_suite_id = d.pop("testSuiteID")

        test_suite_revision = d.pop("testSuiteRevision")

        user_id = d.pop("userID")

        _triggered_via = d.pop("triggeredVia", UNSET)
        triggered_via: Union[Unset, TriggeredVia]
        if isinstance(_triggered_via,  Unset):
            triggered_via = UNSET
        else:
            triggered_via = TriggeredVia(_triggered_via)




        report = cls(
            associated_account=associated_account,
            branch_id=branch_id,
            creation_timestamp=creation_timestamp,
            end_timestamp=end_timestamp,
            last_updated_timestamp=last_updated_timestamp,
            metrics_build_id=metrics_build_id,
            metrics_set_name=metrics_set_name,
            metrics_status=metrics_status,
            name=name,
            org_id=org_id,
            output_location=output_location,
            project_id=project_id,
            report_id=report_id,
            respect_revision_boundary=respect_revision_boundary,
            start_timestamp=start_timestamp,
            status=status,
            status_history=status_history,
            test_suite_id=test_suite_id,
            test_suite_revision=test_suite_revision,
            user_id=user_id,
            triggered_via=triggered_via,
        )


        report.additional_properties = d
        return report

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
