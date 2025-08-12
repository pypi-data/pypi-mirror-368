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
  from ..models.update_experience_tag_fields import UpdateExperienceTagFields





T = TypeVar("T", bound="UpdateExperienceTagInput")


@_attrs_define
class UpdateExperienceTagInput:
    """ 
        Attributes:
            experience_tag (Union[Unset, UpdateExperienceTagFields]):
            update_mask (Union[Unset, List[str]]):
     """

    experience_tag: Union[Unset, 'UpdateExperienceTagFields'] = UNSET
    update_mask: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.update_experience_tag_fields import UpdateExperienceTagFields
        experience_tag: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.experience_tag, Unset):
            experience_tag = self.experience_tag.to_dict()

        update_mask: Union[Unset, List[str]] = UNSET
        if not isinstance(self.update_mask, Unset):
            update_mask = self.update_mask




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if experience_tag is not UNSET:
            field_dict["experienceTag"] = experience_tag
        if update_mask is not UNSET:
            field_dict["updateMask"] = update_mask

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.update_experience_tag_fields import UpdateExperienceTagFields
        d = src_dict.copy()
        _experience_tag = d.pop("experienceTag", UNSET)
        experience_tag: Union[Unset, UpdateExperienceTagFields]
        if isinstance(_experience_tag,  Unset):
            experience_tag = UNSET
        else:
            experience_tag = UpdateExperienceTagFields.from_dict(_experience_tag)




        update_mask = cast(List[str], d.pop("updateMask", UNSET))


        update_experience_tag_input = cls(
            experience_tag=experience_tag,
            update_mask=update_mask,
        )


        update_experience_tag_input.additional_properties = d
        return update_experience_tag_input

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
