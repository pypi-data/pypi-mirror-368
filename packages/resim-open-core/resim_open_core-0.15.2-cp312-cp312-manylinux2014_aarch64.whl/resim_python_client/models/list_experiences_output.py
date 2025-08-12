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
  from ..models.experience import Experience





T = TypeVar("T", bound="ListExperiencesOutput")


@_attrs_define
class ListExperiencesOutput:
    """ 
        Attributes:
            experiences (Union[Unset, List['Experience']]):
            next_page_token (Union[Unset, str]):
            total (Union[Unset, int]):
     """

    experiences: Union[Unset, List['Experience']] = UNSET
    next_page_token: Union[Unset, str] = UNSET
    total: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.experience import Experience
        experiences: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.experiences, Unset):
            experiences = []
            for experiences_item_data in self.experiences:
                experiences_item = experiences_item_data.to_dict()
                experiences.append(experiences_item)



        next_page_token = self.next_page_token

        total = self.total


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if experiences is not UNSET:
            field_dict["experiences"] = experiences
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.experience import Experience
        d = src_dict.copy()
        experiences = []
        _experiences = d.pop("experiences", UNSET)
        for experiences_item_data in (_experiences or []):
            experiences_item = Experience.from_dict(experiences_item_data)



            experiences.append(experiences_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        total = d.pop("total", UNSET)

        list_experiences_output = cls(
            experiences=experiences,
            next_page_token=next_page_token,
            total=total,
        )


        list_experiences_output.additional_properties = d
        return list_experiences_output

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
