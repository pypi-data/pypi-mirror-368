from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

import datetime
from ..models.execution_step import ExecutionStep
from ..models.log_type import LogType
from dateutil.parser import isoparse
from typing import cast
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="Log")


@_attrs_define
class Log:
    """ 
        Attributes:
            checksum (Union[Unset, str]):
            creation_timestamp (Union[Unset, datetime.datetime]):
            execution_step (Union[Unset, ExecutionStep]):
            file_name (Union[Unset, str]):
            file_size (Union[Unset, int]):
            location (Union[Unset, str]):
            log_id (Union[Unset, str]):
            log_output_location (Union[Unset, str]):
            log_type (Union[Unset, LogType]):
            org_id (Union[Unset, str]):
            user_id (Union[Unset, str]):
     """

    checksum: Union[Unset, str] = UNSET
    creation_timestamp: Union[Unset, datetime.datetime] = UNSET
    execution_step: Union[Unset, ExecutionStep] = UNSET
    file_name: Union[Unset, str] = UNSET
    file_size: Union[Unset, int] = UNSET
    location: Union[Unset, str] = UNSET
    log_id: Union[Unset, str] = UNSET
    log_output_location: Union[Unset, str] = UNSET
    log_type: Union[Unset, LogType] = UNSET
    org_id: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        checksum = self.checksum

        creation_timestamp: Union[Unset, str] = UNSET
        if not isinstance(self.creation_timestamp, Unset):
            creation_timestamp = self.creation_timestamp.isoformat()

        execution_step: Union[Unset, str] = UNSET
        if not isinstance(self.execution_step, Unset):
            execution_step = self.execution_step.value


        file_name = self.file_name

        file_size = self.file_size

        location = self.location

        log_id = self.log_id

        log_output_location = self.log_output_location

        log_type: Union[Unset, str] = UNSET
        if not isinstance(self.log_type, Unset):
            log_type = self.log_type.value


        org_id = self.org_id

        user_id = self.user_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if checksum is not UNSET:
            field_dict["checksum"] = checksum
        if creation_timestamp is not UNSET:
            field_dict["creationTimestamp"] = creation_timestamp
        if execution_step is not UNSET:
            field_dict["executionStep"] = execution_step
        if file_name is not UNSET:
            field_dict["fileName"] = file_name
        if file_size is not UNSET:
            field_dict["fileSize"] = file_size
        if location is not UNSET:
            field_dict["location"] = location
        if log_id is not UNSET:
            field_dict["logID"] = log_id
        if log_output_location is not UNSET:
            field_dict["logOutputLocation"] = log_output_location
        if log_type is not UNSET:
            field_dict["logType"] = log_type
        if org_id is not UNSET:
            field_dict["orgID"] = org_id
        if user_id is not UNSET:
            field_dict["userID"] = user_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        checksum = d.pop("checksum", UNSET)

        _creation_timestamp = d.pop("creationTimestamp", UNSET)
        creation_timestamp: Union[Unset, datetime.datetime]
        if isinstance(_creation_timestamp,  Unset):
            creation_timestamp = UNSET
        else:
            creation_timestamp = isoparse(_creation_timestamp)




        _execution_step = d.pop("executionStep", UNSET)
        execution_step: Union[Unset, ExecutionStep]
        if isinstance(_execution_step,  Unset):
            execution_step = UNSET
        else:
            execution_step = ExecutionStep(_execution_step)




        file_name = d.pop("fileName", UNSET)

        file_size = d.pop("fileSize", UNSET)

        location = d.pop("location", UNSET)

        log_id = d.pop("logID", UNSET)

        log_output_location = d.pop("logOutputLocation", UNSET)

        _log_type = d.pop("logType", UNSET)
        log_type: Union[Unset, LogType]
        if isinstance(_log_type,  Unset):
            log_type = UNSET
        else:
            log_type = LogType(_log_type)




        org_id = d.pop("orgID", UNSET)

        user_id = d.pop("userID", UNSET)

        log = cls(
            checksum=checksum,
            creation_timestamp=creation_timestamp,
            execution_step=execution_step,
            file_name=file_name,
            file_size=file_size,
            location=location,
            log_id=log_id,
            log_output_location=log_output_location,
            log_type=log_type,
            org_id=org_id,
            user_id=user_id,
        )


        log.additional_properties = d
        return log

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
