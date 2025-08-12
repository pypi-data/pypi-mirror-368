from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Union
from typing import cast, List
from ..models.metric_status import MetricStatus
import datetime
from typing import cast
from ..types import UNSET, Unset
from typing import cast, Union
from ..models.metric_type import MetricType
from dateutil.parser import isoparse






T = TypeVar("T", bound="BatchMetric")


@_attrs_define
class BatchMetric:
    """ 
        Attributes:
            creation_timestamp (Union[Unset, datetime.datetime]):
            data_i_ds (Union[Unset, List[str]]):
            event_metric (Union[Unset, bool]): true if this metric is for an event
            file_location (Union[Unset, str]):
            metric_id (Union[Unset, str]):
            metric_url (Union[Unset, str]):
            name (Union[Unset, str]):
            org_id (Union[Unset, str]):
            project_id (Union[Unset, str]):
            status (Union[Unset, MetricStatus]):
            type (Union[Unset, MetricType]):
            unit (Union[None, Unset, str]):
            user_id (Union[Unset, str]):
            value (Union[None, Unset, float]):
            batch_id (Union[Unset, str]):
     """

    creation_timestamp: Union[Unset, datetime.datetime] = UNSET
    data_i_ds: Union[Unset, List[str]] = UNSET
    event_metric: Union[Unset, bool] = UNSET
    file_location: Union[Unset, str] = UNSET
    metric_id: Union[Unset, str] = UNSET
    metric_url: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    org_id: Union[Unset, str] = UNSET
    project_id: Union[Unset, str] = UNSET
    status: Union[Unset, MetricStatus] = UNSET
    type: Union[Unset, MetricType] = UNSET
    unit: Union[None, Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    value: Union[None, Unset, float] = UNSET
    batch_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        creation_timestamp: Union[Unset, str] = UNSET
        if not isinstance(self.creation_timestamp, Unset):
            creation_timestamp = self.creation_timestamp.isoformat()

        data_i_ds: Union[Unset, List[str]] = UNSET
        if not isinstance(self.data_i_ds, Unset):
            data_i_ds = self.data_i_ds



        event_metric = self.event_metric

        file_location = self.file_location

        metric_id = self.metric_id

        metric_url = self.metric_url

        name = self.name

        org_id = self.org_id

        project_id = self.project_id

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value


        unit: Union[None, Unset, str]
        if isinstance(self.unit, Unset):
            unit = UNSET
        else:
            unit = self.unit

        user_id = self.user_id

        value: Union[None, Unset, float]
        if isinstance(self.value, Unset):
            value = UNSET
        else:
            value = self.value

        batch_id = self.batch_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if creation_timestamp is not UNSET:
            field_dict["creationTimestamp"] = creation_timestamp
        if data_i_ds is not UNSET:
            field_dict["dataIDs"] = data_i_ds
        if event_metric is not UNSET:
            field_dict["eventMetric"] = event_metric
        if file_location is not UNSET:
            field_dict["fileLocation"] = file_location
        if metric_id is not UNSET:
            field_dict["metricID"] = metric_id
        if metric_url is not UNSET:
            field_dict["metricURL"] = metric_url
        if name is not UNSET:
            field_dict["name"] = name
        if org_id is not UNSET:
            field_dict["orgID"] = org_id
        if project_id is not UNSET:
            field_dict["projectID"] = project_id
        if status is not UNSET:
            field_dict["status"] = status
        if type is not UNSET:
            field_dict["type"] = type
        if unit is not UNSET:
            field_dict["unit"] = unit
        if user_id is not UNSET:
            field_dict["userID"] = user_id
        if value is not UNSET:
            field_dict["value"] = value
        if batch_id is not UNSET:
            field_dict["batchID"] = batch_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _creation_timestamp = d.pop("creationTimestamp", UNSET)
        creation_timestamp: Union[Unset, datetime.datetime]
        if isinstance(_creation_timestamp,  Unset):
            creation_timestamp = UNSET
        else:
            creation_timestamp = isoparse(_creation_timestamp)




        data_i_ds = cast(List[str], d.pop("dataIDs", UNSET))


        event_metric = d.pop("eventMetric", UNSET)

        file_location = d.pop("fileLocation", UNSET)

        metric_id = d.pop("metricID", UNSET)

        metric_url = d.pop("metricURL", UNSET)

        name = d.pop("name", UNSET)

        org_id = d.pop("orgID", UNSET)

        project_id = d.pop("projectID", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, MetricStatus]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = MetricStatus(_status)




        _type = d.pop("type", UNSET)
        type: Union[Unset, MetricType]
        if isinstance(_type,  Unset):
            type = UNSET
        else:
            type = MetricType(_type)




        def _parse_unit(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        unit = _parse_unit(d.pop("unit", UNSET))


        user_id = d.pop("userID", UNSET)

        def _parse_value(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        value = _parse_value(d.pop("value", UNSET))


        batch_id = d.pop("batchID", UNSET)

        batch_metric = cls(
            creation_timestamp=creation_timestamp,
            data_i_ds=data_i_ds,
            event_metric=event_metric,
            file_location=file_location,
            metric_id=metric_id,
            metric_url=metric_url,
            name=name,
            org_id=org_id,
            project_id=project_id,
            status=status,
            type=type,
            unit=unit,
            user_id=user_id,
            value=value,
            batch_id=batch_id,
        )


        batch_metric.additional_properties = d
        return batch_metric

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
