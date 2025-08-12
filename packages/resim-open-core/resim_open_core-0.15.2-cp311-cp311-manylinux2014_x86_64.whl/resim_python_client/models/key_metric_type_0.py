from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from typing import cast
from typing import cast, List
from typing import cast, Union

if TYPE_CHECKING:
  from ..models.first_build_metric_type_0 import FirstBuildMetricType0
  from ..models.key_metric_target_type_0 import KeyMetricTargetType0
  from ..models.key_metric_performance_point import KeyMetricPerformancePoint





T = TypeVar("T", bound="KeyMetricType0")


@_attrs_define
class KeyMetricType0:
    """ 
        Attributes:
            first_build_metric (Union['FirstBuildMetricType0', None]): The first batch metric in the sequence, and some info
                about how it has changed
            latest_value (float):  Example: 150.
            name (str):  Example: Meal Planning Time.
            performance (List['KeyMetricPerformancePoint']):
            target (Union['KeyMetricTargetType0', None]): The optional desired target for this metric
            unit (Union[None, str]):  Example: Seconds.
     """

    first_build_metric: Union['FirstBuildMetricType0', None]
    latest_value: float
    name: str
    performance: List['KeyMetricPerformancePoint']
    target: Union['KeyMetricTargetType0', None]
    unit: Union[None, str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.first_build_metric_type_0 import FirstBuildMetricType0
        from ..models.key_metric_target_type_0 import KeyMetricTargetType0
        from ..models.key_metric_performance_point import KeyMetricPerformancePoint
        first_build_metric: Union[Dict[str, Any], None]
        if isinstance(self.first_build_metric, FirstBuildMetricType0):
            first_build_metric = self.first_build_metric.to_dict()
        else:
            first_build_metric = self.first_build_metric

        latest_value = self.latest_value

        name = self.name

        performance = []
        for performance_item_data in self.performance:
            performance_item = performance_item_data.to_dict()
            performance.append(performance_item)



        target: Union[Dict[str, Any], None]
        if isinstance(self.target, KeyMetricTargetType0):
            target = self.target.to_dict()
        else:
            target = self.target

        unit: Union[None, str]
        unit = self.unit


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "firstBuildMetric": first_build_metric,
            "latestValue": latest_value,
            "name": name,
            "performance": performance,
            "target": target,
            "unit": unit,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.first_build_metric_type_0 import FirstBuildMetricType0
        from ..models.key_metric_target_type_0 import KeyMetricTargetType0
        from ..models.key_metric_performance_point import KeyMetricPerformancePoint
        d = src_dict.copy()
        def _parse_first_build_metric(data: object) -> Union['FirstBuildMetricType0', None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasfirst_build_metric_type_0 = FirstBuildMetricType0.from_dict(data)



                return componentsschemasfirst_build_metric_type_0
            except: # noqa: E722
                pass
            return cast(Union['FirstBuildMetricType0', None], data)

        first_build_metric = _parse_first_build_metric(d.pop("firstBuildMetric"))


        latest_value = d.pop("latestValue")

        name = d.pop("name")

        performance = []
        _performance = d.pop("performance")
        for performance_item_data in (_performance):
            performance_item = KeyMetricPerformancePoint.from_dict(performance_item_data)



            performance.append(performance_item)


        def _parse_target(data: object) -> Union['KeyMetricTargetType0', None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemaskey_metric_target_type_0 = KeyMetricTargetType0.from_dict(data)



                return componentsschemaskey_metric_target_type_0
            except: # noqa: E722
                pass
            return cast(Union['KeyMetricTargetType0', None], data)

        target = _parse_target(d.pop("target"))


        def _parse_unit(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        unit = _parse_unit(d.pop("unit"))


        key_metric_type_0 = cls(
            first_build_metric=first_build_metric,
            latest_value=latest_value,
            name=name,
            performance=performance,
            target=target,
            unit=unit,
        )


        key_metric_type_0.additional_properties = d
        return key_metric_type_0

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
