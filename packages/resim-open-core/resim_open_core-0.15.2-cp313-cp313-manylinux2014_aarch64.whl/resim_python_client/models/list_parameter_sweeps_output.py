from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import cast, List
from ..types import UNSET, Unset
from typing import Union
from typing import Dict

if TYPE_CHECKING:
  from ..models.parameter_sweep import ParameterSweep





T = TypeVar("T", bound="ListParameterSweepsOutput")


@_attrs_define
class ListParameterSweepsOutput:
    """ 
        Attributes:
            next_page_token (Union[Unset, str]):
            sweeps (Union[Unset, List['ParameterSweep']]):
     """

    next_page_token: Union[Unset, str] = UNSET
    sweeps: Union[Unset, List['ParameterSweep']] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.parameter_sweep import ParameterSweep
        next_page_token = self.next_page_token

        sweeps: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.sweeps, Unset):
            sweeps = []
            for sweeps_item_data in self.sweeps:
                sweeps_item = sweeps_item_data.to_dict()
                sweeps.append(sweeps_item)




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if sweeps is not UNSET:
            field_dict["sweeps"] = sweeps

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.parameter_sweep import ParameterSweep
        d = src_dict.copy()
        next_page_token = d.pop("nextPageToken", UNSET)

        sweeps = []
        _sweeps = d.pop("sweeps", UNSET)
        for sweeps_item_data in (_sweeps or []):
            sweeps_item = ParameterSweep.from_dict(sweeps_item_data)



            sweeps.append(sweeps_item)


        list_parameter_sweeps_output = cls(
            next_page_token=next_page_token,
            sweeps=sweeps,
        )


        list_parameter_sweeps_output.additional_properties = d
        return list_parameter_sweeps_output

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
