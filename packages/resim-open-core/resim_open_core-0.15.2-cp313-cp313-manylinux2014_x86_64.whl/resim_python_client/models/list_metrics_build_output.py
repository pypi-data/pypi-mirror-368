from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from typing import cast, List
from typing import cast

if TYPE_CHECKING:
  from ..models.metrics_build import MetricsBuild





T = TypeVar("T", bound="ListMetricsBuildOutput")


@_attrs_define
class ListMetricsBuildOutput:
    """ 
        Attributes:
            metrics_builds (List['MetricsBuild']):
            next_page_token (str):
            total (int):
     """

    metrics_builds: List['MetricsBuild']
    next_page_token: str
    total: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.metrics_build import MetricsBuild
        metrics_builds = []
        for metrics_builds_item_data in self.metrics_builds:
            metrics_builds_item = metrics_builds_item_data.to_dict()
            metrics_builds.append(metrics_builds_item)



        next_page_token = self.next_page_token

        total = self.total


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "metricsBuilds": metrics_builds,
            "nextPageToken": next_page_token,
            "total": total,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.metrics_build import MetricsBuild
        d = src_dict.copy()
        metrics_builds = []
        _metrics_builds = d.pop("metricsBuilds")
        for metrics_builds_item_data in (_metrics_builds):
            metrics_builds_item = MetricsBuild.from_dict(metrics_builds_item_data)



            metrics_builds.append(metrics_builds_item)


        next_page_token = d.pop("nextPageToken")

        total = d.pop("total")

        list_metrics_build_output = cls(
            metrics_builds=metrics_builds,
            next_page_token=next_page_token,
            total=total,
        )


        list_metrics_build_output.additional_properties = d
        return list_metrics_build_output

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
