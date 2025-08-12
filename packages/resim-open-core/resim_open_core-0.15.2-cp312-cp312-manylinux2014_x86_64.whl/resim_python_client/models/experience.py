from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
import datetime
from typing import cast
from typing import Dict
from dateutil.parser import isoparse

if TYPE_CHECKING:
  from ..models.environment_variable import EnvironmentVariable





T = TypeVar("T", bound="Experience")


@_attrs_define
class Experience:
    """ 
        Attributes:
            archived (bool):
            container_timeout_seconds (int):
            creation_timestamp (datetime.datetime):
            description (str):
            environment_variables (List['EnvironmentVariable']):
            experience_id (str):
            location (str): [DEPRECATED] This field was previously used to report an experience's location. Experiences can
                now be defined with multiple locations, this field will display the first location; this field will be removed
                in a future version.
            locations (List[str]):
            name (str):
            org_id (str):
            profile (str):
            project_id (str):
            user_id (str):
     """

    archived: bool
    container_timeout_seconds: int
    creation_timestamp: datetime.datetime
    description: str
    environment_variables: List['EnvironmentVariable']
    experience_id: str
    location: str
    locations: List[str]
    name: str
    org_id: str
    profile: str
    project_id: str
    user_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.environment_variable import EnvironmentVariable
        archived = self.archived

        container_timeout_seconds = self.container_timeout_seconds

        creation_timestamp = self.creation_timestamp.isoformat()

        description = self.description

        environment_variables = []
        for environment_variables_item_data in self.environment_variables:
            environment_variables_item = environment_variables_item_data.to_dict()
            environment_variables.append(environment_variables_item)



        experience_id = self.experience_id

        location = self.location

        locations = self.locations



        name = self.name

        org_id = self.org_id

        profile = self.profile

        project_id = self.project_id

        user_id = self.user_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "archived": archived,
            "containerTimeoutSeconds": container_timeout_seconds,
            "creationTimestamp": creation_timestamp,
            "description": description,
            "environmentVariables": environment_variables,
            "experienceID": experience_id,
            "location": location,
            "locations": locations,
            "name": name,
            "orgID": org_id,
            "profile": profile,
            "projectID": project_id,
            "userID": user_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.environment_variable import EnvironmentVariable
        d = src_dict.copy()
        archived = d.pop("archived")

        container_timeout_seconds = d.pop("containerTimeoutSeconds")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        description = d.pop("description")

        environment_variables = []
        _environment_variables = d.pop("environmentVariables")
        for environment_variables_item_data in (_environment_variables):
            environment_variables_item = EnvironmentVariable.from_dict(environment_variables_item_data)



            environment_variables.append(environment_variables_item)


        experience_id = d.pop("experienceID")

        location = d.pop("location")

        locations = cast(List[str], d.pop("locations"))


        name = d.pop("name")

        org_id = d.pop("orgID")

        profile = d.pop("profile")

        project_id = d.pop("projectID")

        user_id = d.pop("userID")

        experience = cls(
            archived=archived,
            container_timeout_seconds=container_timeout_seconds,
            creation_timestamp=creation_timestamp,
            description=description,
            environment_variables=environment_variables,
            experience_id=experience_id,
            location=location,
            locations=locations,
            name=name,
            org_id=org_id,
            profile=profile,
            project_id=project_id,
            user_id=user_id,
        )


        experience.additional_properties = d
        return experience

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
