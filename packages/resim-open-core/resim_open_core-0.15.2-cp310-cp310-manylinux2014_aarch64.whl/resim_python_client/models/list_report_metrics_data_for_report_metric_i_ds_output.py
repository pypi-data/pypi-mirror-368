from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Union
from typing import cast, List
from ..types import UNSET, Unset
from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.report_metrics_data_and_i_ds import ReportMetricsDataAndIDs





T = TypeVar("T", bound="ListReportMetricsDataForReportMetricIDsOutput")


@_attrs_define
class ListReportMetricsDataForReportMetricIDsOutput:
    """ 
        Attributes:
            next_page_token (Union[Unset, str]):
            report_metrics_data_and_i_ds (Union[Unset, List['ReportMetricsDataAndIDs']]):
     """

    next_page_token: Union[Unset, str] = UNSET
    report_metrics_data_and_i_ds: Union[Unset, List['ReportMetricsDataAndIDs']] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.report_metrics_data_and_i_ds import ReportMetricsDataAndIDs
        next_page_token = self.next_page_token

        report_metrics_data_and_i_ds: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.report_metrics_data_and_i_ds, Unset):
            report_metrics_data_and_i_ds = []
            for report_metrics_data_and_i_ds_item_data in self.report_metrics_data_and_i_ds:
                report_metrics_data_and_i_ds_item = report_metrics_data_and_i_ds_item_data.to_dict()
                report_metrics_data_and_i_ds.append(report_metrics_data_and_i_ds_item)




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if report_metrics_data_and_i_ds is not UNSET:
            field_dict["reportMetricsDataAndIDs"] = report_metrics_data_and_i_ds

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.report_metrics_data_and_i_ds import ReportMetricsDataAndIDs
        d = src_dict.copy()
        next_page_token = d.pop("nextPageToken", UNSET)

        report_metrics_data_and_i_ds = []
        _report_metrics_data_and_i_ds = d.pop("reportMetricsDataAndIDs", UNSET)
        for report_metrics_data_and_i_ds_item_data in (_report_metrics_data_and_i_ds or []):
            report_metrics_data_and_i_ds_item = ReportMetricsDataAndIDs.from_dict(report_metrics_data_and_i_ds_item_data)



            report_metrics_data_and_i_ds.append(report_metrics_data_and_i_ds_item)


        list_report_metrics_data_for_report_metric_i_ds_output = cls(
            next_page_token=next_page_token,
            report_metrics_data_and_i_ds=report_metrics_data_and_i_ds,
        )


        list_report_metrics_data_for_report_metric_i_ds_output.additional_properties = d
        return list_report_metrics_data_for_report_metric_i_ds_output

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
