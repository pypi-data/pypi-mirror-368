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
  from ..models.environment_variable import EnvironmentVariable





T = TypeVar("T", bound="UpdateExperienceFields")


@_attrs_define
class UpdateExperienceFields:
    """ 
        Attributes:
            container_timeout_seconds (Union[Unset, int]):
            description (Union[Unset, str]):
            environment_variables (Union[Unset, List['EnvironmentVariable']]):
            experience_tag_i_ds (Union[Unset, List[str]]):
            location (Union[Unset, str]): [DEPRECATED] This field was previously used to define an experience's location.
                Experiences can now be defined with multiple locations, using the locations field. This field will be removed in
                a future version.
            locations (Union[Unset, List[str]]):
            name (Union[Unset, str]):
            profile (Union[Unset, str]):
            system_i_ds (Union[Unset, List[str]]):
     """

    container_timeout_seconds: Union[Unset, int] = UNSET
    description: Union[Unset, str] = UNSET
    environment_variables: Union[Unset, List['EnvironmentVariable']] = UNSET
    experience_tag_i_ds: Union[Unset, List[str]] = UNSET
    location: Union[Unset, str] = UNSET
    locations: Union[Unset, List[str]] = UNSET
    name: Union[Unset, str] = UNSET
    profile: Union[Unset, str] = UNSET
    system_i_ds: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.environment_variable import EnvironmentVariable
        container_timeout_seconds = self.container_timeout_seconds

        description = self.description

        environment_variables: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.environment_variables, Unset):
            environment_variables = []
            for environment_variables_item_data in self.environment_variables:
                environment_variables_item = environment_variables_item_data.to_dict()
                environment_variables.append(environment_variables_item)



        experience_tag_i_ds: Union[Unset, List[str]] = UNSET
        if not isinstance(self.experience_tag_i_ds, Unset):
            experience_tag_i_ds = self.experience_tag_i_ds



        location = self.location

        locations: Union[Unset, List[str]] = UNSET
        if not isinstance(self.locations, Unset):
            locations = self.locations



        name = self.name

        profile = self.profile

        system_i_ds: Union[Unset, List[str]] = UNSET
        if not isinstance(self.system_i_ds, Unset):
            system_i_ds = self.system_i_ds




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if container_timeout_seconds is not UNSET:
            field_dict["containerTimeoutSeconds"] = container_timeout_seconds
        if description is not UNSET:
            field_dict["description"] = description
        if environment_variables is not UNSET:
            field_dict["environmentVariables"] = environment_variables
        if experience_tag_i_ds is not UNSET:
            field_dict["experienceTagIDs"] = experience_tag_i_ds
        if location is not UNSET:
            field_dict["location"] = location
        if locations is not UNSET:
            field_dict["locations"] = locations
        if name is not UNSET:
            field_dict["name"] = name
        if profile is not UNSET:
            field_dict["profile"] = profile
        if system_i_ds is not UNSET:
            field_dict["systemIDs"] = system_i_ds

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.environment_variable import EnvironmentVariable
        d = src_dict.copy()
        container_timeout_seconds = d.pop("containerTimeoutSeconds", UNSET)

        description = d.pop("description", UNSET)

        environment_variables = []
        _environment_variables = d.pop("environmentVariables", UNSET)
        for environment_variables_item_data in (_environment_variables or []):
            environment_variables_item = EnvironmentVariable.from_dict(environment_variables_item_data)



            environment_variables.append(environment_variables_item)


        experience_tag_i_ds = cast(List[str], d.pop("experienceTagIDs", UNSET))


        location = d.pop("location", UNSET)

        locations = cast(List[str], d.pop("locations", UNSET))


        name = d.pop("name", UNSET)

        profile = d.pop("profile", UNSET)

        system_i_ds = cast(List[str], d.pop("systemIDs", UNSET))


        update_experience_fields = cls(
            container_timeout_seconds=container_timeout_seconds,
            description=description,
            environment_variables=environment_variables,
            experience_tag_i_ds=experience_tag_i_ds,
            location=location,
            locations=locations,
            name=name,
            profile=profile,
            system_i_ds=system_i_ds,
        )


        update_experience_fields.additional_properties = d
        return update_experience_fields

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
