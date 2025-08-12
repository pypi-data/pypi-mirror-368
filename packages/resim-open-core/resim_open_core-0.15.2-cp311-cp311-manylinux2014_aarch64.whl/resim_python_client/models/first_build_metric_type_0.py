from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
import datetime
from dateutil.parser import isoparse






T = TypeVar("T", bound="FirstBuildMetricType0")


@_attrs_define
class FirstBuildMetricType0:
    """ The first batch metric in the sequence, and some info about how it has changed

        Attributes:
            delta (float):
            time (datetime.datetime):
            value (float):  Example: -120.234.
     """

    delta: float
    time: datetime.datetime
    value: float
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        delta = self.delta

        time = self.time.isoformat()

        value = self.value


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "delta": delta,
            "time": time,
            "value": value,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        delta = d.pop("delta")

        time = isoparse(d.pop("time"))




        value = d.pop("value")

        first_build_metric_type_0 = cls(
            delta=delta,
            time=time,
            value=value,
        )


        first_build_metric_type_0.additional_properties = d
        return first_build_metric_type_0

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
