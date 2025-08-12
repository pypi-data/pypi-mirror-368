from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Union
from typing import cast, List
from typing import cast
from ..types import UNSET, Unset
from typing import Dict

if TYPE_CHECKING:
  from ..models.metrics_data import MetricsData





T = TypeVar("T", bound="ListReportMetricsDataOutput")


@_attrs_define
class ListReportMetricsDataOutput:
    """ 
        Attributes:
            next_page_token (Union[Unset, str]):
            report_metrics_data (Union[Unset, List['MetricsData']]):
     """

    next_page_token: Union[Unset, str] = UNSET
    report_metrics_data: Union[Unset, List['MetricsData']] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.metrics_data import MetricsData
        next_page_token = self.next_page_token

        report_metrics_data: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.report_metrics_data, Unset):
            report_metrics_data = []
            for report_metrics_data_item_data in self.report_metrics_data:
                report_metrics_data_item = report_metrics_data_item_data.to_dict()
                report_metrics_data.append(report_metrics_data_item)




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if report_metrics_data is not UNSET:
            field_dict["reportMetricsData"] = report_metrics_data

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.metrics_data import MetricsData
        d = src_dict.copy()
        next_page_token = d.pop("nextPageToken", UNSET)

        report_metrics_data = []
        _report_metrics_data = d.pop("reportMetricsData", UNSET)
        for report_metrics_data_item_data in (_report_metrics_data or []):
            report_metrics_data_item = MetricsData.from_dict(report_metrics_data_item_data)



            report_metrics_data.append(report_metrics_data_item)


        list_report_metrics_data_output = cls(
            next_page_token=next_page_token,
            report_metrics_data=report_metrics_data,
        )


        list_report_metrics_data_output.additional_properties = d
        return list_report_metrics_data_output

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
