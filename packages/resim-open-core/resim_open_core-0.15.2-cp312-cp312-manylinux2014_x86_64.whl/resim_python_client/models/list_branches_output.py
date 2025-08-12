from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
from typing import Union
from typing import cast
from ..types import UNSET, Unset
from typing import Dict

if TYPE_CHECKING:
  from ..models.branch import Branch





T = TypeVar("T", bound="ListBranchesOutput")


@_attrs_define
class ListBranchesOutput:
    """ 
        Attributes:
            branches (Union[Unset, List['Branch']]):
            next_page_token (Union[Unset, str]):
     """

    branches: Union[Unset, List['Branch']] = UNSET
    next_page_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.branch import Branch
        branches: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.branches, Unset):
            branches = []
            for branches_item_data in self.branches:
                branches_item = branches_item_data.to_dict()
                branches.append(branches_item)



        next_page_token = self.next_page_token


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if branches is not UNSET:
            field_dict["branches"] = branches
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.branch import Branch
        d = src_dict.copy()
        branches = []
        _branches = d.pop("branches", UNSET)
        for branches_item_data in (_branches or []):
            branches_item = Branch.from_dict(branches_item_data)



            branches.append(branches_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_branches_output = cls(
            branches=branches,
            next_page_token=next_page_token,
        )


        list_branches_output.additional_properties = d
        return list_branches_output

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
