from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Union
from typing import cast, List
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Dict

if TYPE_CHECKING:
  from ..models.experience_filter_input import ExperienceFilterInput





T = TypeVar("T", bound="ReviseTestSuiteInput")


@_attrs_define
class ReviseTestSuiteInput:
    """ 
        Attributes:
            update_metrics_build (bool):
            adhoc (Union[Unset, bool]):
            all_experiences (Union[Unset, bool]):
            description (Union[Unset, str]):
            excluded_experience_i_ds (Union[Unset, List[str]]):
            experiences (Union[Unset, List[str]]):
            filters (Union[Unset, ExperienceFilterInput]):
            metrics_build_id (Union[Unset, str]):
            metrics_set_name (Union[None, Unset, str]):
            name (Union[Unset, str]):
            show_on_summary (Union[Unset, bool]):
            system_id (Union[Unset, str]):
     """

    update_metrics_build: bool
    adhoc: Union[Unset, bool] = UNSET
    all_experiences: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    excluded_experience_i_ds: Union[Unset, List[str]] = UNSET
    experiences: Union[Unset, List[str]] = UNSET
    filters: Union[Unset, 'ExperienceFilterInput'] = UNSET
    metrics_build_id: Union[Unset, str] = UNSET
    metrics_set_name: Union[None, Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    show_on_summary: Union[Unset, bool] = UNSET
    system_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.experience_filter_input import ExperienceFilterInput
        update_metrics_build = self.update_metrics_build

        adhoc = self.adhoc

        all_experiences = self.all_experiences

        description = self.description

        excluded_experience_i_ds: Union[Unset, List[str]] = UNSET
        if not isinstance(self.excluded_experience_i_ds, Unset):
            excluded_experience_i_ds = self.excluded_experience_i_ds



        experiences: Union[Unset, List[str]] = UNSET
        if not isinstance(self.experiences, Unset):
            experiences = self.experiences



        filters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()

        metrics_build_id = self.metrics_build_id

        metrics_set_name: Union[None, Unset, str]
        if isinstance(self.metrics_set_name, Unset):
            metrics_set_name = UNSET
        else:
            metrics_set_name = self.metrics_set_name

        name = self.name

        show_on_summary = self.show_on_summary

        system_id = self.system_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "updateMetricsBuild": update_metrics_build,
        })
        if adhoc is not UNSET:
            field_dict["adhoc"] = adhoc
        if all_experiences is not UNSET:
            field_dict["allExperiences"] = all_experiences
        if description is not UNSET:
            field_dict["description"] = description
        if excluded_experience_i_ds is not UNSET:
            field_dict["excludedExperienceIDs"] = excluded_experience_i_ds
        if experiences is not UNSET:
            field_dict["experiences"] = experiences
        if filters is not UNSET:
            field_dict["filters"] = filters
        if metrics_build_id is not UNSET:
            field_dict["metricsBuildID"] = metrics_build_id
        if metrics_set_name is not UNSET:
            field_dict["metricsSetName"] = metrics_set_name
        if name is not UNSET:
            field_dict["name"] = name
        if show_on_summary is not UNSET:
            field_dict["show_on_summary"] = show_on_summary
        if system_id is not UNSET:
            field_dict["systemID"] = system_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.experience_filter_input import ExperienceFilterInput
        d = src_dict.copy()
        update_metrics_build = d.pop("updateMetricsBuild")

        adhoc = d.pop("adhoc", UNSET)

        all_experiences = d.pop("allExperiences", UNSET)

        description = d.pop("description", UNSET)

        excluded_experience_i_ds = cast(List[str], d.pop("excludedExperienceIDs", UNSET))


        experiences = cast(List[str], d.pop("experiences", UNSET))


        _filters = d.pop("filters", UNSET)
        filters: Union[Unset, ExperienceFilterInput]
        if isinstance(_filters,  Unset):
            filters = UNSET
        else:
            filters = ExperienceFilterInput.from_dict(_filters)




        metrics_build_id = d.pop("metricsBuildID", UNSET)

        def _parse_metrics_set_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        metrics_set_name = _parse_metrics_set_name(d.pop("metricsSetName", UNSET))


        name = d.pop("name", UNSET)

        show_on_summary = d.pop("show_on_summary", UNSET)

        system_id = d.pop("systemID", UNSET)

        revise_test_suite_input = cls(
            update_metrics_build=update_metrics_build,
            adhoc=adhoc,
            all_experiences=all_experiences,
            description=description,
            excluded_experience_i_ds=excluded_experience_i_ds,
            experiences=experiences,
            filters=filters,
            metrics_build_id=metrics_build_id,
            metrics_set_name=metrics_set_name,
            name=name,
            show_on_summary=show_on_summary,
            system_id=system_id,
        )


        revise_test_suite_input.additional_properties = d
        return revise_test_suite_input

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
