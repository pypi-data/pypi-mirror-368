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
  from ..models.batch_metric import BatchMetric





T = TypeVar("T", bound="ListBatchMetricsOutput")


@_attrs_define
class ListBatchMetricsOutput:
    """ 
        Attributes:
            batch_metrics (Union[Unset, List['BatchMetric']]):
            next_page_token (Union[Unset, str]):
     """

    batch_metrics: Union[Unset, List['BatchMetric']] = UNSET
    next_page_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.batch_metric import BatchMetric
        batch_metrics: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.batch_metrics, Unset):
            batch_metrics = []
            for batch_metrics_item_data in self.batch_metrics:
                batch_metrics_item = batch_metrics_item_data.to_dict()
                batch_metrics.append(batch_metrics_item)



        next_page_token = self.next_page_token


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batch_metrics is not UNSET:
            field_dict["batchMetrics"] = batch_metrics
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.batch_metric import BatchMetric
        d = src_dict.copy()
        batch_metrics = []
        _batch_metrics = d.pop("batchMetrics", UNSET)
        for batch_metrics_item_data in (_batch_metrics or []):
            batch_metrics_item = BatchMetric.from_dict(batch_metrics_item_data)



            batch_metrics.append(batch_metrics_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_batch_metrics_output = cls(
            batch_metrics=batch_metrics,
            next_page_token=next_page_token,
        )


        list_batch_metrics_output.additional_properties = d
        return list_batch_metrics_output

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
