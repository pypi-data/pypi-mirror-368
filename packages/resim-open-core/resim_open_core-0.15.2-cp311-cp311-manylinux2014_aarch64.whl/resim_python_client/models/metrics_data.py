from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.metrics_data_type import MetricsDataType
from ..types import UNSET, Unset
from typing import cast, Union
from typing import cast
from dateutil.parser import isoparse
import datetime
from typing import Union






T = TypeVar("T", bound="MetricsData")


@_attrs_define
class MetricsData:
    """ 
        Attributes:
            creation_timestamp (Union[Unset, datetime.datetime]):
            data_id (Union[Unset, str]):
            file_location (Union[Unset, str]):
            filename (Union[None, Unset, str]):
            metrics_data_type (Union[Unset, MetricsDataType]):
            metrics_data_url (Union[Unset, str]):
            name (Union[Unset, str]):
            org_id (Union[Unset, str]):
            user_id (Union[Unset, str]):
     """

    creation_timestamp: Union[Unset, datetime.datetime] = UNSET
    data_id: Union[Unset, str] = UNSET
    file_location: Union[Unset, str] = UNSET
    filename: Union[None, Unset, str] = UNSET
    metrics_data_type: Union[Unset, MetricsDataType] = UNSET
    metrics_data_url: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    org_id: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        creation_timestamp: Union[Unset, str] = UNSET
        if not isinstance(self.creation_timestamp, Unset):
            creation_timestamp = self.creation_timestamp.isoformat()

        data_id = self.data_id

        file_location = self.file_location

        filename: Union[None, Unset, str]
        if isinstance(self.filename, Unset):
            filename = UNSET
        else:
            filename = self.filename

        metrics_data_type: Union[Unset, str] = UNSET
        if not isinstance(self.metrics_data_type, Unset):
            metrics_data_type = self.metrics_data_type.value


        metrics_data_url = self.metrics_data_url

        name = self.name

        org_id = self.org_id

        user_id = self.user_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if creation_timestamp is not UNSET:
            field_dict["creationTimestamp"] = creation_timestamp
        if data_id is not UNSET:
            field_dict["dataID"] = data_id
        if file_location is not UNSET:
            field_dict["fileLocation"] = file_location
        if filename is not UNSET:
            field_dict["filename"] = filename
        if metrics_data_type is not UNSET:
            field_dict["metricsDataType"] = metrics_data_type
        if metrics_data_url is not UNSET:
            field_dict["metricsDataURL"] = metrics_data_url
        if name is not UNSET:
            field_dict["name"] = name
        if org_id is not UNSET:
            field_dict["orgID"] = org_id
        if user_id is not UNSET:
            field_dict["userID"] = user_id

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




        data_id = d.pop("dataID", UNSET)

        file_location = d.pop("fileLocation", UNSET)

        def _parse_filename(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        filename = _parse_filename(d.pop("filename", UNSET))


        _metrics_data_type = d.pop("metricsDataType", UNSET)
        metrics_data_type: Union[Unset, MetricsDataType]
        if isinstance(_metrics_data_type,  Unset):
            metrics_data_type = UNSET
        else:
            metrics_data_type = MetricsDataType(_metrics_data_type)




        metrics_data_url = d.pop("metricsDataURL", UNSET)

        name = d.pop("name", UNSET)

        org_id = d.pop("orgID", UNSET)

        user_id = d.pop("userID", UNSET)

        metrics_data = cls(
            creation_timestamp=creation_timestamp,
            data_id=data_id,
            file_location=file_location,
            filename=filename,
            metrics_data_type=metrics_data_type,
            metrics_data_url=metrics_data_url,
            name=name,
            org_id=org_id,
            user_id=user_id,
        )


        metrics_data.additional_properties = d
        return metrics_data

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
