from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from ..types import UNSET, Unset
from typing import cast
from typing import cast, List
from typing import Union

if TYPE_CHECKING:
  from ..models.experience_filter_input import ExperienceFilterInput





T = TypeVar("T", bound="AddTagsToExperiencesInput")


@_attrs_define
class AddTagsToExperiencesInput:
    """ 
        Attributes:
            experience_tag_i_ds (List[str]):
            all_experiences (Union[Unset, bool]):
            experiences (Union[Unset, List[str]]):
            filters (Union[Unset, ExperienceFilterInput]):
     """

    experience_tag_i_ds: List[str]
    all_experiences: Union[Unset, bool] = UNSET
    experiences: Union[Unset, List[str]] = UNSET
    filters: Union[Unset, 'ExperienceFilterInput'] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.experience_filter_input import ExperienceFilterInput
        experience_tag_i_ds = self.experience_tag_i_ds



        all_experiences = self.all_experiences

        experiences: Union[Unset, List[str]] = UNSET
        if not isinstance(self.experiences, Unset):
            experiences = self.experiences



        filters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "experienceTagIDs": experience_tag_i_ds,
        })
        if all_experiences is not UNSET:
            field_dict["allExperiences"] = all_experiences
        if experiences is not UNSET:
            field_dict["experiences"] = experiences
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.experience_filter_input import ExperienceFilterInput
        d = src_dict.copy()
        experience_tag_i_ds = cast(List[str], d.pop("experienceTagIDs"))


        all_experiences = d.pop("allExperiences", UNSET)

        experiences = cast(List[str], d.pop("experiences", UNSET))


        _filters = d.pop("filters", UNSET)
        filters: Union[Unset, ExperienceFilterInput]
        if isinstance(_filters,  Unset):
            filters = UNSET
        else:
            filters = ExperienceFilterInput.from_dict(_filters)




        add_tags_to_experiences_input = cls(
            experience_tag_i_ds=experience_tag_i_ds,
            all_experiences=all_experiences,
            experiences=experiences,
            filters=filters,
        )


        add_tags_to_experiences_input.additional_properties = d
        return add_tags_to_experiences_input

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
