from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Union
from ..types import UNSET, Unset






T = TypeVar("T", bound="CustomMetric")


@_attrs_define
class CustomMetric:
    """ 
        Attributes:
            name (str):  Example: Planning time.
            value (float):  Example: 0.01253.
            unit (Union[Unset, str]):  Example: Seconds.
     """

    name: str
    value: float
    unit: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        value = self.value

        unit = self.unit


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "value": value,
        })
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        value = d.pop("value")

        unit = d.pop("unit", UNSET)

        custom_metric = cls(
            name=name,
            value=value,
            unit=unit,
        )


        custom_metric.additional_properties = d
        return custom_metric

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
