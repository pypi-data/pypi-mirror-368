from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
import datetime
from dateutil.parser import isoparse






T = TypeVar("T", bound="System")


@_attrs_define
class System:
    """ 
        Attributes:
            archived (bool):
            build_gpus (int):
            build_memory_mib (int):
            build_shared_memory_mb (int):
            build_vcpus (int):
            creation_timestamp (datetime.datetime):
            description (str):
            metrics_build_gpus (int):
            metrics_build_memory_mib (int):
            metrics_build_shared_memory_mb (int):
            metrics_build_vcpus (int):
            name (str):
            num_batches (int):
            num_builds (int):
            num_experiences (int):
            num_metrics_builds (int):
            num_test_suites (int):
            org_id (str):
            project_id (str):
            system_id (str):
            user_id (str):
     """

    archived: bool
    build_gpus: int
    build_memory_mib: int
    build_shared_memory_mb: int
    build_vcpus: int
    creation_timestamp: datetime.datetime
    description: str
    metrics_build_gpus: int
    metrics_build_memory_mib: int
    metrics_build_shared_memory_mb: int
    metrics_build_vcpus: int
    name: str
    num_batches: int
    num_builds: int
    num_experiences: int
    num_metrics_builds: int
    num_test_suites: int
    org_id: str
    project_id: str
    system_id: str
    user_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        archived = self.archived

        build_gpus = self.build_gpus

        build_memory_mib = self.build_memory_mib

        build_shared_memory_mb = self.build_shared_memory_mb

        build_vcpus = self.build_vcpus

        creation_timestamp = self.creation_timestamp.isoformat()

        description = self.description

        metrics_build_gpus = self.metrics_build_gpus

        metrics_build_memory_mib = self.metrics_build_memory_mib

        metrics_build_shared_memory_mb = self.metrics_build_shared_memory_mb

        metrics_build_vcpus = self.metrics_build_vcpus

        name = self.name

        num_batches = self.num_batches

        num_builds = self.num_builds

        num_experiences = self.num_experiences

        num_metrics_builds = self.num_metrics_builds

        num_test_suites = self.num_test_suites

        org_id = self.org_id

        project_id = self.project_id

        system_id = self.system_id

        user_id = self.user_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "archived": archived,
            "build_gpus": build_gpus,
            "build_memory_mib": build_memory_mib,
            "build_shared_memory_mb": build_shared_memory_mb,
            "build_vcpus": build_vcpus,
            "creationTimestamp": creation_timestamp,
            "description": description,
            "metrics_build_gpus": metrics_build_gpus,
            "metrics_build_memory_mib": metrics_build_memory_mib,
            "metrics_build_shared_memory_mb": metrics_build_shared_memory_mb,
            "metrics_build_vcpus": metrics_build_vcpus,
            "name": name,
            "numBatches": num_batches,
            "numBuilds": num_builds,
            "numExperiences": num_experiences,
            "numMetricsBuilds": num_metrics_builds,
            "numTestSuites": num_test_suites,
            "orgID": org_id,
            "projectID": project_id,
            "systemID": system_id,
            "userID": user_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        archived = d.pop("archived")

        build_gpus = d.pop("build_gpus")

        build_memory_mib = d.pop("build_memory_mib")

        build_shared_memory_mb = d.pop("build_shared_memory_mb")

        build_vcpus = d.pop("build_vcpus")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        description = d.pop("description")

        metrics_build_gpus = d.pop("metrics_build_gpus")

        metrics_build_memory_mib = d.pop("metrics_build_memory_mib")

        metrics_build_shared_memory_mb = d.pop("metrics_build_shared_memory_mb")

        metrics_build_vcpus = d.pop("metrics_build_vcpus")

        name = d.pop("name")

        num_batches = d.pop("numBatches")

        num_builds = d.pop("numBuilds")

        num_experiences = d.pop("numExperiences")

        num_metrics_builds = d.pop("numMetricsBuilds")

        num_test_suites = d.pop("numTestSuites")

        org_id = d.pop("orgID")

        project_id = d.pop("projectID")

        system_id = d.pop("systemID")

        user_id = d.pop("userID")

        system = cls(
            archived=archived,
            build_gpus=build_gpus,
            build_memory_mib=build_memory_mib,
            build_shared_memory_mb=build_shared_memory_mb,
            build_vcpus=build_vcpus,
            creation_timestamp=creation_timestamp,
            description=description,
            metrics_build_gpus=metrics_build_gpus,
            metrics_build_memory_mib=metrics_build_memory_mib,
            metrics_build_shared_memory_mb=metrics_build_shared_memory_mb,
            metrics_build_vcpus=metrics_build_vcpus,
            name=name,
            num_batches=num_batches,
            num_builds=num_builds,
            num_experiences=num_experiences,
            num_metrics_builds=num_metrics_builds,
            num_test_suites=num_test_suites,
            org_id=org_id,
            project_id=project_id,
            system_id=system_id,
            user_id=user_id,
        )


        system.additional_properties = d
        return system

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
