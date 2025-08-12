from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union
from typing import Dict
from typing import cast

if TYPE_CHECKING:
  from ..models.job_metrics_data import JobMetricsData





T = TypeVar("T", bound="MetricsDataAndMetricID")


@_attrs_define
class MetricsDataAndMetricID:
    """ 
        Attributes:
            metric_id (Union[Unset, str]):
            metrics_data (Union[Unset, JobMetricsData]):
     """

    metric_id: Union[Unset, str] = UNSET
    metrics_data: Union[Unset, 'JobMetricsData'] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.job_metrics_data import JobMetricsData
        metric_id = self.metric_id

        metrics_data: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metrics_data, Unset):
            metrics_data = self.metrics_data.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if metric_id is not UNSET:
            field_dict["metricID"] = metric_id
        if metrics_data is not UNSET:
            field_dict["metricsData"] = metrics_data

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.job_metrics_data import JobMetricsData
        d = src_dict.copy()
        metric_id = d.pop("metricID", UNSET)

        _metrics_data = d.pop("metricsData", UNSET)
        metrics_data: Union[Unset, JobMetricsData]
        if isinstance(_metrics_data,  Unset):
            metrics_data = UNSET
        else:
            metrics_data = JobMetricsData.from_dict(_metrics_data)




        metrics_data_and_metric_id = cls(
            metric_id=metric_id,
            metrics_data=metrics_data,
        )


        metrics_data_and_metric_id.additional_properties = d
        return metrics_data_and_metric_id

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
