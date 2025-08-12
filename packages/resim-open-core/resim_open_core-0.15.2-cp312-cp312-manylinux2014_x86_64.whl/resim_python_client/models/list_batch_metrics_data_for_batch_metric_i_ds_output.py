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
  from ..models.batch_metrics_data_and_i_ds import BatchMetricsDataAndIDs





T = TypeVar("T", bound="ListBatchMetricsDataForBatchMetricIDsOutput")


@_attrs_define
class ListBatchMetricsDataForBatchMetricIDsOutput:
    """ 
        Attributes:
            batch_metrics_data_and_i_ds (Union[Unset, List['BatchMetricsDataAndIDs']]):
            next_page_token (Union[Unset, str]):
     """

    batch_metrics_data_and_i_ds: Union[Unset, List['BatchMetricsDataAndIDs']] = UNSET
    next_page_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.batch_metrics_data_and_i_ds import BatchMetricsDataAndIDs
        batch_metrics_data_and_i_ds: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.batch_metrics_data_and_i_ds, Unset):
            batch_metrics_data_and_i_ds = []
            for batch_metrics_data_and_i_ds_item_data in self.batch_metrics_data_and_i_ds:
                batch_metrics_data_and_i_ds_item = batch_metrics_data_and_i_ds_item_data.to_dict()
                batch_metrics_data_and_i_ds.append(batch_metrics_data_and_i_ds_item)



        next_page_token = self.next_page_token


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batch_metrics_data_and_i_ds is not UNSET:
            field_dict["batchMetricsDataAndIDs"] = batch_metrics_data_and_i_ds
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.batch_metrics_data_and_i_ds import BatchMetricsDataAndIDs
        d = src_dict.copy()
        batch_metrics_data_and_i_ds = []
        _batch_metrics_data_and_i_ds = d.pop("batchMetricsDataAndIDs", UNSET)
        for batch_metrics_data_and_i_ds_item_data in (_batch_metrics_data_and_i_ds or []):
            batch_metrics_data_and_i_ds_item = BatchMetricsDataAndIDs.from_dict(batch_metrics_data_and_i_ds_item_data)



            batch_metrics_data_and_i_ds.append(batch_metrics_data_and_i_ds_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_batch_metrics_data_for_batch_metric_i_ds_output = cls(
            batch_metrics_data_and_i_ds=batch_metrics_data_and_i_ds,
            next_page_token=next_page_token,
        )


        list_batch_metrics_data_for_batch_metric_i_ds_output.additional_properties = d
        return list_batch_metrics_data_for_batch_metric_i_ds_output

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
