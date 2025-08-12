from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from ..models.metric_status import MetricStatus
from typing import cast, List
from dateutil.parser import isoparse
from ..models.event_timestamp_type import EventTimestampType
import datetime






T = TypeVar("T", bound="Event")


@_attrs_define
class Event:
    """ 
        Attributes:
            creation_timestamp (datetime.datetime):
            description (str):
            event_id (str):
            metrics_i_ds (List[str]):
            name (str):
            status (MetricStatus):
            tags (List[str]):  Example: ['tag1', 'tag2'].
            timestamp (datetime.datetime):
            timestamp_type (EventTimestampType):
     """

    creation_timestamp: datetime.datetime
    description: str
    event_id: str
    metrics_i_ds: List[str]
    name: str
    status: MetricStatus
    tags: List[str]
    timestamp: datetime.datetime
    timestamp_type: EventTimestampType
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        creation_timestamp = self.creation_timestamp.isoformat()

        description = self.description

        event_id = self.event_id

        metrics_i_ds = self.metrics_i_ds



        name = self.name

        status = self.status.value

        tags = self.tags



        timestamp = self.timestamp.isoformat()

        timestamp_type = self.timestamp_type.value


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "creationTimestamp": creation_timestamp,
            "description": description,
            "eventID": event_id,
            "metricsIDs": metrics_i_ds,
            "name": name,
            "status": status,
            "tags": tags,
            "timestamp": timestamp,
            "timestampType": timestamp_type,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        description = d.pop("description")

        event_id = d.pop("eventID")

        metrics_i_ds = cast(List[str], d.pop("metricsIDs"))


        name = d.pop("name")

        status = MetricStatus(d.pop("status"))




        tags = cast(List[str], d.pop("tags"))


        timestamp = isoparse(d.pop("timestamp"))




        timestamp_type = EventTimestampType(d.pop("timestampType"))




        event = cls(
            creation_timestamp=creation_timestamp,
            description=description,
            event_id=event_id,
            metrics_i_ds=metrics_i_ds,
            name=name,
            status=status,
            tags=tags,
            timestamp=timestamp,
            timestamp_type=timestamp_type,
        )


        event.additional_properties = d
        return event

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
