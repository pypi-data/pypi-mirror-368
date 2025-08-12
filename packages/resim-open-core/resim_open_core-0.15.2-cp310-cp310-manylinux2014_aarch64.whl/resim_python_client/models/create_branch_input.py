from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.branch_type import BranchType






T = TypeVar("T", bound="CreateBranchInput")


@_attrs_define
class CreateBranchInput:
    """ 
        Attributes:
            branch_type (BranchType):
            name (str):
     """

    branch_type: BranchType
    name: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        branch_type = self.branch_type.value

        name = self.name


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "branchType": branch_type,
            "name": name,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        branch_type = BranchType(d.pop("branchType"))




        name = d.pop("name")

        create_branch_input = cls(
            branch_type=branch_type,
            name=name,
        )


        create_branch_input.additional_properties = d
        return create_branch_input

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
