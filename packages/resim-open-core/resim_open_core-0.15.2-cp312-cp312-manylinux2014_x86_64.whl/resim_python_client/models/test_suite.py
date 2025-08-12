from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
from typing import Union
import datetime
from typing import cast
from ..types import UNSET, Unset
from typing import cast, Union
from dateutil.parser import isoparse






T = TypeVar("T", bound="TestSuite")


@_attrs_define
class TestSuite:
    """ 
        Attributes:
            archived (bool):
            creation_timestamp (datetime.datetime):
            description (str):
            experiences (List[str]):
            name (str):
            org_id (str):
            project_id (str):
            show_on_summary (bool):
            system_id (str):
            test_suite_id (str):
            test_suite_revision (int):
            user_id (str):
            metrics_build_id (Union[Unset, str]):
            metrics_set_name (Union[None, Unset, str]):
            summary_reference_date (Union[Unset, datetime.datetime]):
     """

    archived: bool
    creation_timestamp: datetime.datetime
    description: str
    experiences: List[str]
    name: str
    org_id: str
    project_id: str
    show_on_summary: bool
    system_id: str
    test_suite_id: str
    test_suite_revision: int
    user_id: str
    metrics_build_id: Union[Unset, str] = UNSET
    metrics_set_name: Union[None, Unset, str] = UNSET
    summary_reference_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        archived = self.archived

        creation_timestamp = self.creation_timestamp.isoformat()

        description = self.description

        experiences = self.experiences



        name = self.name

        org_id = self.org_id

        project_id = self.project_id

        show_on_summary = self.show_on_summary

        system_id = self.system_id

        test_suite_id = self.test_suite_id

        test_suite_revision = self.test_suite_revision

        user_id = self.user_id

        metrics_build_id = self.metrics_build_id

        metrics_set_name: Union[None, Unset, str]
        if isinstance(self.metrics_set_name, Unset):
            metrics_set_name = UNSET
        else:
            metrics_set_name = self.metrics_set_name

        summary_reference_date: Union[Unset, str] = UNSET
        if not isinstance(self.summary_reference_date, Unset):
            summary_reference_date = self.summary_reference_date.isoformat()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "archived": archived,
            "creationTimestamp": creation_timestamp,
            "description": description,
            "experiences": experiences,
            "name": name,
            "orgID": org_id,
            "projectID": project_id,
            "showOnSummary": show_on_summary,
            "systemID": system_id,
            "testSuiteID": test_suite_id,
            "testSuiteRevision": test_suite_revision,
            "userID": user_id,
        })
        if metrics_build_id is not UNSET:
            field_dict["metricsBuildID"] = metrics_build_id
        if metrics_set_name is not UNSET:
            field_dict["metricsSetName"] = metrics_set_name
        if summary_reference_date is not UNSET:
            field_dict["summaryReferenceDate"] = summary_reference_date

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        archived = d.pop("archived")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        description = d.pop("description")

        experiences = cast(List[str], d.pop("experiences"))


        name = d.pop("name")

        org_id = d.pop("orgID")

        project_id = d.pop("projectID")

        show_on_summary = d.pop("showOnSummary")

        system_id = d.pop("systemID")

        test_suite_id = d.pop("testSuiteID")

        test_suite_revision = d.pop("testSuiteRevision")

        user_id = d.pop("userID")

        metrics_build_id = d.pop("metricsBuildID", UNSET)

        def _parse_metrics_set_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        metrics_set_name = _parse_metrics_set_name(d.pop("metricsSetName", UNSET))


        _summary_reference_date = d.pop("summaryReferenceDate", UNSET)
        summary_reference_date: Union[Unset, datetime.datetime]
        if isinstance(_summary_reference_date,  Unset):
            summary_reference_date = UNSET
        else:
            summary_reference_date = isoparse(_summary_reference_date)




        test_suite = cls(
            archived=archived,
            creation_timestamp=creation_timestamp,
            description=description,
            experiences=experiences,
            name=name,
            org_id=org_id,
            project_id=project_id,
            show_on_summary=show_on_summary,
            system_id=system_id,
            test_suite_id=test_suite_id,
            test_suite_revision=test_suite_revision,
            user_id=user_id,
            metrics_build_id=metrics_build_id,
            metrics_set_name=metrics_set_name,
            summary_reference_date=summary_reference_date,
        )


        test_suite.additional_properties = d
        return test_suite

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
