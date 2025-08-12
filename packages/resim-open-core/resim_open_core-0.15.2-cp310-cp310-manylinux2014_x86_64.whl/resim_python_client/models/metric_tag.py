from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Union
from ..types import UNSET, Unset
import datetime
from typing import cast
from dateutil.parser import isoparse






T = TypeVar("T", bound="MetricTag")


@_attrs_define
class MetricTag:
    """ 
        Attributes:
            creation_timestamp (datetime.datetime):
            name (str):
            tag_id (str):
            value (str):
            metric_id (Union[Unset, str]):
     """

    creation_timestamp: datetime.datetime
    name: str
    tag_id: str
    value: str
    metric_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        creation_timestamp = self.creation_timestamp.isoformat()

        name = self.name

        tag_id = self.tag_id

        value = self.value

        metric_id = self.metric_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "creationTimestamp": creation_timestamp,
            "name": name,
            "tagID": tag_id,
            "value": value,
        })
        if metric_id is not UNSET:
            field_dict["metricID"] = metric_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        name = d.pop("name")

        tag_id = d.pop("tagID")

        value = d.pop("value")

        metric_id = d.pop("metricID", UNSET)

        metric_tag = cls(
            creation_timestamp=creation_timestamp,
            name=name,
            tag_id=tag_id,
            value=value,
            metric_id=metric_id,
        )


        metric_tag.additional_properties = d
        return metric_tag

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
