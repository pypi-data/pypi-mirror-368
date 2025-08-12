from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="CreateSystemInput")


@_attrs_define
class CreateSystemInput:
    """ 
        Attributes:
            build_gpus (int):
            build_memory_mib (int):
            build_shared_memory_mb (int):
            build_vcpus (int):
            description (str):
            metrics_build_gpus (int):
            metrics_build_memory_mib (int):
            metrics_build_shared_memory_mb (int):
            metrics_build_vcpus (int):
            name (str):
     """

    build_gpus: int
    build_memory_mib: int
    build_shared_memory_mb: int
    build_vcpus: int
    description: str
    metrics_build_gpus: int
    metrics_build_memory_mib: int
    metrics_build_shared_memory_mb: int
    metrics_build_vcpus: int
    name: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        build_gpus = self.build_gpus

        build_memory_mib = self.build_memory_mib

        build_shared_memory_mb = self.build_shared_memory_mb

        build_vcpus = self.build_vcpus

        description = self.description

        metrics_build_gpus = self.metrics_build_gpus

        metrics_build_memory_mib = self.metrics_build_memory_mib

        metrics_build_shared_memory_mb = self.metrics_build_shared_memory_mb

        metrics_build_vcpus = self.metrics_build_vcpus

        name = self.name


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "build_gpus": build_gpus,
            "build_memory_mib": build_memory_mib,
            "build_shared_memory_mb": build_shared_memory_mb,
            "build_vcpus": build_vcpus,
            "description": description,
            "metrics_build_gpus": metrics_build_gpus,
            "metrics_build_memory_mib": metrics_build_memory_mib,
            "metrics_build_shared_memory_mb": metrics_build_shared_memory_mb,
            "metrics_build_vcpus": metrics_build_vcpus,
            "name": name,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        build_gpus = d.pop("build_gpus")

        build_memory_mib = d.pop("build_memory_mib")

        build_shared_memory_mb = d.pop("build_shared_memory_mb")

        build_vcpus = d.pop("build_vcpus")

        description = d.pop("description")

        metrics_build_gpus = d.pop("metrics_build_gpus")

        metrics_build_memory_mib = d.pop("metrics_build_memory_mib")

        metrics_build_shared_memory_mb = d.pop("metrics_build_shared_memory_mb")

        metrics_build_vcpus = d.pop("metrics_build_vcpus")

        name = d.pop("name")

        create_system_input = cls(
            build_gpus=build_gpus,
            build_memory_mib=build_memory_mib,
            build_shared_memory_mb=build_shared_memory_mb,
            build_vcpus=build_vcpus,
            description=description,
            metrics_build_gpus=metrics_build_gpus,
            metrics_build_memory_mib=metrics_build_memory_mib,
            metrics_build_shared_memory_mb=metrics_build_shared_memory_mb,
            metrics_build_vcpus=metrics_build_vcpus,
            name=name,
        )


        create_system_input.additional_properties = d
        return create_system_input

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
