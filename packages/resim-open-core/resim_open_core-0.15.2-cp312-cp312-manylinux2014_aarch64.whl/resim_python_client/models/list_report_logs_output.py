from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
from typing import Union
from typing import cast
from ..types import UNSET, Unset
from typing import Dict

if TYPE_CHECKING:
  from ..models.report_log import ReportLog





T = TypeVar("T", bound="ListReportLogsOutput")


@_attrs_define
class ListReportLogsOutput:
    """ 
        Attributes:
            logs (Union[Unset, List['ReportLog']]):
            next_page_token (Union[Unset, str]):
     """

    logs: Union[Unset, List['ReportLog']] = UNSET
    next_page_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.report_log import ReportLog
        logs: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.logs, Unset):
            logs = []
            for logs_item_data in self.logs:
                logs_item = logs_item_data.to_dict()
                logs.append(logs_item)



        next_page_token = self.next_page_token


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if logs is not UNSET:
            field_dict["logs"] = logs
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.report_log import ReportLog
        d = src_dict.copy()
        logs = []
        _logs = d.pop("logs", UNSET)
        for logs_item_data in (_logs or []):
            logs_item = ReportLog.from_dict(logs_item_data)



            logs.append(logs_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_report_logs_output = cls(
            logs=logs,
            next_page_token=next_page_token,
        )


        list_report_logs_output.additional_properties = d
        return list_report_logs_output

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
