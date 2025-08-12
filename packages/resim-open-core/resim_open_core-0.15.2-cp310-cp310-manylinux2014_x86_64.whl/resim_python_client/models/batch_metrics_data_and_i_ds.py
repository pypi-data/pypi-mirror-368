from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union
from typing import Dict

if TYPE_CHECKING:
  from ..models.batch_metrics_data import BatchMetricsData





T = TypeVar("T", bound="BatchMetricsDataAndIDs")


@_attrs_define
class BatchMetricsDataAndIDs:
    """ 
        Attributes:
            batch_metric_id (Union[Unset, str]):
            batch_metrics_data (Union[Unset, BatchMetricsData]):
     """

    batch_metric_id: Union[Unset, str] = UNSET
    batch_metrics_data: Union[Unset, 'BatchMetricsData'] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.batch_metrics_data import BatchMetricsData
        batch_metric_id = self.batch_metric_id

        batch_metrics_data: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.batch_metrics_data, Unset):
            batch_metrics_data = self.batch_metrics_data.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batch_metric_id is not UNSET:
            field_dict["batchMetricID"] = batch_metric_id
        if batch_metrics_data is not UNSET:
            field_dict["batchMetricsData"] = batch_metrics_data

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.batch_metrics_data import BatchMetricsData
        d = src_dict.copy()
        batch_metric_id = d.pop("batchMetricID", UNSET)

        _batch_metrics_data = d.pop("batchMetricsData", UNSET)
        batch_metrics_data: Union[Unset, BatchMetricsData]
        if isinstance(_batch_metrics_data,  Unset):
            batch_metrics_data = UNSET
        else:
            batch_metrics_data = BatchMetricsData.from_dict(_batch_metrics_data)




        batch_metrics_data_and_i_ds = cls(
            batch_metric_id=batch_metric_id,
            batch_metrics_data=batch_metrics_data,
        )


        batch_metrics_data_and_i_ds.additional_properties = d
        return batch_metrics_data_and_i_ds

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
