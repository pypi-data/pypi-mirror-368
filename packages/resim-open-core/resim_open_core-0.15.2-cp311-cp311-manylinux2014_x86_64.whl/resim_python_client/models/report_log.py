from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.log_type import LogType
from typing import cast
import datetime
from dateutil.parser import isoparse






T = TypeVar("T", bound="ReportLog")


@_attrs_define
class ReportLog:
    """ 
        Attributes:
            checksum (str):
            creation_timestamp (datetime.datetime):
            file_name (str):
            file_size (int):
            location (str):
            log_id (str):
            log_output_location (str):
            log_type (LogType):
            org_id (str):
            user_id (str):
     """

    checksum: str
    creation_timestamp: datetime.datetime
    file_name: str
    file_size: int
    location: str
    log_id: str
    log_output_location: str
    log_type: LogType
    org_id: str
    user_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        checksum = self.checksum

        creation_timestamp = self.creation_timestamp.isoformat()

        file_name = self.file_name

        file_size = self.file_size

        location = self.location

        log_id = self.log_id

        log_output_location = self.log_output_location

        log_type = self.log_type.value

        org_id = self.org_id

        user_id = self.user_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "checksum": checksum,
            "creationTimestamp": creation_timestamp,
            "fileName": file_name,
            "fileSize": file_size,
            "location": location,
            "logID": log_id,
            "logOutputLocation": log_output_location,
            "logType": log_type,
            "orgID": org_id,
            "userID": user_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        checksum = d.pop("checksum")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        file_name = d.pop("fileName")

        file_size = d.pop("fileSize")

        location = d.pop("location")

        log_id = d.pop("logID")

        log_output_location = d.pop("logOutputLocation")

        log_type = LogType(d.pop("logType"))




        org_id = d.pop("orgID")

        user_id = d.pop("userID")

        report_log = cls(
            checksum=checksum,
            creation_timestamp=creation_timestamp,
            file_name=file_name,
            file_size=file_size,
            location=location,
            log_id=log_id,
            log_output_location=log_output_location,
            log_type=log_type,
            org_id=org_id,
            user_id=user_id,
        )


        report_log.additional_properties = d
        return report_log

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
