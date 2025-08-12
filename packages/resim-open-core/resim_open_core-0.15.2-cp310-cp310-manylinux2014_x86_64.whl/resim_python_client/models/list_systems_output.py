from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Union
from typing import cast, List
from ..types import UNSET, Unset
from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.system import System





T = TypeVar("T", bound="ListSystemsOutput")


@_attrs_define
class ListSystemsOutput:
    """ 
        Attributes:
            next_page_token (Union[Unset, str]):
            systems (Union[Unset, List['System']]):
     """

    next_page_token: Union[Unset, str] = UNSET
    systems: Union[Unset, List['System']] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.system import System
        next_page_token = self.next_page_token

        systems: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.systems, Unset):
            systems = []
            for systems_item_data in self.systems:
                systems_item = systems_item_data.to_dict()
                systems.append(systems_item)




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if systems is not UNSET:
            field_dict["systems"] = systems

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.system import System
        d = src_dict.copy()
        next_page_token = d.pop("nextPageToken", UNSET)

        systems = []
        _systems = d.pop("systems", UNSET)
        for systems_item_data in (_systems or []):
            systems_item = System.from_dict(systems_item_data)



            systems.append(systems_item)


        list_systems_output = cls(
            next_page_token=next_page_token,
            systems=systems,
        )


        list_systems_output.additional_properties = d
        return list_systems_output

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
