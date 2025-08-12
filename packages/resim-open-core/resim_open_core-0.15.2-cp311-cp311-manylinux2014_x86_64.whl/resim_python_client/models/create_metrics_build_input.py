from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="CreateMetricsBuildInput")


@_attrs_define
class CreateMetricsBuildInput:
    """ 
        Attributes:
            image_uri (str):
            name (str):
            version (str):
     """

    image_uri: str
    name: str
    version: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        image_uri = self.image_uri

        name = self.name

        version = self.version


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "imageUri": image_uri,
            "name": name,
            "version": version,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        image_uri = d.pop("imageUri")

        name = d.pop("name")

        version = d.pop("version")

        create_metrics_build_input = cls(
            image_uri=image_uri,
            name=name,
            version=version,
        )


        create_metrics_build_input.additional_properties = d
        return create_metrics_build_input

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
