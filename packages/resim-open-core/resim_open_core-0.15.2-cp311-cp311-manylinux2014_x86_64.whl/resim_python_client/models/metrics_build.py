from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
import datetime
from dateutil.parser import isoparse






T = TypeVar("T", bound="MetricsBuild")


@_attrs_define
class MetricsBuild:
    """ 
        Attributes:
            creation_timestamp (datetime.datetime):
            image_uri (str):
            metrics_build_id (str):
            name (str):
            org_id (str):
            project_id (str):
            user_id (str):
            version (str):
     """

    creation_timestamp: datetime.datetime
    image_uri: str
    metrics_build_id: str
    name: str
    org_id: str
    project_id: str
    user_id: str
    version: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        creation_timestamp = self.creation_timestamp.isoformat()

        image_uri = self.image_uri

        metrics_build_id = self.metrics_build_id

        name = self.name

        org_id = self.org_id

        project_id = self.project_id

        user_id = self.user_id

        version = self.version


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "creationTimestamp": creation_timestamp,
            "imageUri": image_uri,
            "metricsBuildID": metrics_build_id,
            "name": name,
            "orgID": org_id,
            "projectID": project_id,
            "userID": user_id,
            "version": version,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        image_uri = d.pop("imageUri")

        metrics_build_id = d.pop("metricsBuildID")

        name = d.pop("name")

        org_id = d.pop("orgID")

        project_id = d.pop("projectID")

        user_id = d.pop("userID")

        version = d.pop("version")

        metrics_build = cls(
            creation_timestamp=creation_timestamp,
            image_uri=image_uri,
            metrics_build_id=metrics_build_id,
            name=name,
            org_id=org_id,
            project_id=project_id,
            user_id=user_id,
            version=version,
        )


        metrics_build.additional_properties = d
        return metrics_build

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
