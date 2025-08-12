from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from ..models.branch_type import BranchType
import datetime
from dateutil.parser import isoparse






T = TypeVar("T", bound="Branch")


@_attrs_define
class Branch:
    """ 
        Attributes:
            branch_id (str):
            branch_type (BranchType):
            creation_timestamp (datetime.datetime):
            name (str):
            org_id (str):
            project_id (str):
            user_id (str):
     """

    branch_id: str
    branch_type: BranchType
    creation_timestamp: datetime.datetime
    name: str
    org_id: str
    project_id: str
    user_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        branch_id = self.branch_id

        branch_type = self.branch_type.value

        creation_timestamp = self.creation_timestamp.isoformat()

        name = self.name

        org_id = self.org_id

        project_id = self.project_id

        user_id = self.user_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "branchID": branch_id,
            "branchType": branch_type,
            "creationTimestamp": creation_timestamp,
            "name": name,
            "orgID": org_id,
            "projectID": project_id,
            "userID": user_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        branch_id = d.pop("branchID")

        branch_type = BranchType(d.pop("branchType"))




        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        name = d.pop("name")

        org_id = d.pop("orgID")

        project_id = d.pop("projectID")

        user_id = d.pop("userID")

        branch = cls(
            branch_id=branch_id,
            branch_type=branch_type,
            creation_timestamp=creation_timestamp,
            name=name,
            org_id=org_id,
            project_id=project_id,
            user_id=user_id,
        )


        branch.additional_properties = d
        return branch

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
