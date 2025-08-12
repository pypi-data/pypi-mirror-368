from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union
from typing import cast, List






T = TypeVar("T", bound="RerunBatchInput")


@_attrs_define
class RerunBatchInput:
    """ 
        Attributes:
            job_i_ds (Union[Unset, List[str]]):
     """

    job_i_ds: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        job_i_ds: Union[Unset, List[str]] = UNSET
        if not isinstance(self.job_i_ds, Unset):
            job_i_ds = self.job_i_ds




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if job_i_ds is not UNSET:
            field_dict["jobIDs"] = job_i_ds

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        job_i_ds = cast(List[str], d.pop("jobIDs", UNSET))


        rerun_batch_input = cls(
            job_i_ds=job_i_ds,
        )


        rerun_batch_input.additional_properties = d
        return rerun_batch_input

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
