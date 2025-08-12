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
  from ..models.update_build_fields import UpdateBuildFields





T = TypeVar("T", bound="UpdateBuildInput")


@_attrs_define
class UpdateBuildInput:
    """ 
        Attributes:
            build (Union[Unset, UpdateBuildFields]):
            update_mask (Union[Unset, List[str]]):
     """

    build: Union[Unset, 'UpdateBuildFields'] = UNSET
    update_mask: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.update_build_fields import UpdateBuildFields
        build: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.build, Unset):
            build = self.build.to_dict()

        update_mask: Union[Unset, List[str]] = UNSET
        if not isinstance(self.update_mask, Unset):
            update_mask = self.update_mask




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if build is not UNSET:
            field_dict["build"] = build
        if update_mask is not UNSET:
            field_dict["updateMask"] = update_mask

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.update_build_fields import UpdateBuildFields
        d = src_dict.copy()
        _build = d.pop("build", UNSET)
        build: Union[Unset, UpdateBuildFields]
        if isinstance(_build,  Unset):
            build = UNSET
        else:
            build = UpdateBuildFields.from_dict(_build)




        update_mask = cast(List[str], d.pop("updateMask", UNSET))


        update_build_input = cls(
            build=build,
            update_mask=update_mask,
        )


        update_build_input.additional_properties = d
        return update_build_input

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
