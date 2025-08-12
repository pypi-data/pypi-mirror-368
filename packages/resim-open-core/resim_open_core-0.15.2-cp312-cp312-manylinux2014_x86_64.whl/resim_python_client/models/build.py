from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

import datetime
from typing import cast
from dateutil.parser import isoparse






T = TypeVar("T", bound="Build")


@_attrs_define
class Build:
    """ 
        Attributes:
            associated_account (str):
            branch_id (str):
            build_id (str):
            build_specification (str): Build spec in YAML format.
            creation_timestamp (datetime.datetime):
            description (str): The description of the build. May be a SHA or commit message.
            image_uri (str):
            name (str): The name of the build.
            org_id (str):
            project_id (str):
            system_id (str):
            user_id (str):
            version (str):
     """

    associated_account: str
    branch_id: str
    build_id: str
    build_specification: str
    creation_timestamp: datetime.datetime
    description: str
    image_uri: str
    name: str
    org_id: str
    project_id: str
    system_id: str
    user_id: str
    version: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        associated_account = self.associated_account

        branch_id = self.branch_id

        build_id = self.build_id

        build_specification = self.build_specification

        creation_timestamp = self.creation_timestamp.isoformat()

        description = self.description

        image_uri = self.image_uri

        name = self.name

        org_id = self.org_id

        project_id = self.project_id

        system_id = self.system_id

        user_id = self.user_id

        version = self.version


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "associatedAccount": associated_account,
            "branchID": branch_id,
            "buildID": build_id,
            "buildSpecification": build_specification,
            "creationTimestamp": creation_timestamp,
            "description": description,
            "imageUri": image_uri,
            "name": name,
            "orgID": org_id,
            "projectID": project_id,
            "systemID": system_id,
            "userID": user_id,
            "version": version,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        associated_account = d.pop("associatedAccount")

        branch_id = d.pop("branchID")

        build_id = d.pop("buildID")

        build_specification = d.pop("buildSpecification")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        description = d.pop("description")

        image_uri = d.pop("imageUri")

        name = d.pop("name")

        org_id = d.pop("orgID")

        project_id = d.pop("projectID")

        system_id = d.pop("systemID")

        user_id = d.pop("userID")

        version = d.pop("version")

        build = cls(
            associated_account=associated_account,
            branch_id=branch_id,
            build_id=build_id,
            build_specification=build_specification,
            creation_timestamp=creation_timestamp,
            description=description,
            image_uri=image_uri,
            name=name,
            org_id=org_id,
            project_id=project_id,
            system_id=system_id,
            user_id=user_id,
            version=version,
        )


        build.additional_properties = d
        return build

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
