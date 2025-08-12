from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
from typing import Union
from typing import cast
from ..types import UNSET, Unset
from typing import Dict

if TYPE_CHECKING:
  from ..models.job import Job





T = TypeVar("T", bound="ListAllJobsOutput")


@_attrs_define
class ListAllJobsOutput:
    """ 
        Attributes:
            jobs (Union[Unset, List['Job']]):
            next_page_token (Union[Unset, str]):
            total (Union[Unset, int]):
     """

    jobs: Union[Unset, List['Job']] = UNSET
    next_page_token: Union[Unset, str] = UNSET
    total: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.job import Job
        jobs: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.jobs, Unset):
            jobs = []
            for jobs_item_data in self.jobs:
                jobs_item = jobs_item_data.to_dict()
                jobs.append(jobs_item)



        next_page_token = self.next_page_token

        total = self.total


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if jobs is not UNSET:
            field_dict["jobs"] = jobs
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.job import Job
        d = src_dict.copy()
        jobs = []
        _jobs = d.pop("jobs", UNSET)
        for jobs_item_data in (_jobs or []):
            jobs_item = Job.from_dict(jobs_item_data)



            jobs.append(jobs_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        total = d.pop("total", UNSET)

        list_all_jobs_output = cls(
            jobs=jobs,
            next_page_token=next_page_token,
            total=total,
        )


        list_all_jobs_output.additional_properties = d
        return list_all_jobs_output

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
