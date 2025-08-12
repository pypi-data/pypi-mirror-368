from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from ..types import UNSET, Unset
from typing import cast
from typing import cast, List
from typing import Union

if TYPE_CHECKING:
  from ..models.metric import Metric





T = TypeVar("T", bound="ListReportMetricsOutput")


@_attrs_define
class ListReportMetricsOutput:
    """ 
        Attributes:
            next_page_token (Union[Unset, str]):
            report_metrics (Union[Unset, List['Metric']]):
     """

    next_page_token: Union[Unset, str] = UNSET
    report_metrics: Union[Unset, List['Metric']] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.metric import Metric
        next_page_token = self.next_page_token

        report_metrics: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.report_metrics, Unset):
            report_metrics = []
            for report_metrics_item_data in self.report_metrics:
                report_metrics_item = report_metrics_item_data.to_dict()
                report_metrics.append(report_metrics_item)




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if report_metrics is not UNSET:
            field_dict["reportMetrics"] = report_metrics

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.metric import Metric
        d = src_dict.copy()
        next_page_token = d.pop("nextPageToken", UNSET)

        report_metrics = []
        _report_metrics = d.pop("reportMetrics", UNSET)
        for report_metrics_item_data in (_report_metrics or []):
            report_metrics_item = Metric.from_dict(report_metrics_item_data)



            report_metrics.append(report_metrics_item)


        list_report_metrics_output = cls(
            next_page_token=next_page_token,
            report_metrics=report_metrics,
        )


        list_report_metrics_output.additional_properties = d
        return list_report_metrics_output

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
