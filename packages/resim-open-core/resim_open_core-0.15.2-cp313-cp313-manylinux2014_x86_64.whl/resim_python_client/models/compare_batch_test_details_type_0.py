from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.conflated_job_status import ConflatedJobStatus
from typing import cast, Union






T = TypeVar("T", bound="CompareBatchTestDetailsType0")


@_attrs_define
class CompareBatchTestDetailsType0:
    """ 
        Attributes:
            job_id (str):
            num_metrics (Union[None, int]): The number of failblock/failwarn/passing metrics (based on job's status).
                Otherwise this will be null
            status (ConflatedJobStatus):
     """

    job_id: str
    num_metrics: Union[None, int]
    status: ConflatedJobStatus
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        job_id = self.job_id

        num_metrics: Union[None, int]
        num_metrics = self.num_metrics

        status = self.status.value


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "jobID": job_id,
            "numMetrics": num_metrics,
            "status": status,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        job_id = d.pop("jobID")

        def _parse_num_metrics(data: object) -> Union[None, int]:
            if data is None:
                return data
            return cast(Union[None, int], data)

        num_metrics = _parse_num_metrics(d.pop("numMetrics"))


        status = ConflatedJobStatus(d.pop("status"))




        compare_batch_test_details_type_0 = cls(
            job_id=job_id,
            num_metrics=num_metrics,
            status=status,
        )


        compare_batch_test_details_type_0.additional_properties = d
        return compare_batch_test_details_type_0

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
