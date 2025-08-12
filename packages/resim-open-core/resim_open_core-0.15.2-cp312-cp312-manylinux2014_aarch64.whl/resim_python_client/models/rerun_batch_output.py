from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Union
from ..types import UNSET, Unset
from typing import cast, List






T = TypeVar("T", bound="RerunBatchOutput")


@_attrs_define
class RerunBatchOutput:
    """ 
        Attributes:
            batch_id (Union[Unset, str]):
            job_i_ds (Union[Unset, List[str]]):
            run_counter (Union[Unset, int]):
     """

    batch_id: Union[Unset, str] = UNSET
    job_i_ds: Union[Unset, List[str]] = UNSET
    run_counter: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        batch_id = self.batch_id

        job_i_ds: Union[Unset, List[str]] = UNSET
        if not isinstance(self.job_i_ds, Unset):
            job_i_ds = self.job_i_ds



        run_counter = self.run_counter


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batch_id is not UNSET:
            field_dict["batchID"] = batch_id
        if job_i_ds is not UNSET:
            field_dict["jobIDs"] = job_i_ds
        if run_counter is not UNSET:
            field_dict["runCounter"] = run_counter

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        batch_id = d.pop("batchID", UNSET)

        job_i_ds = cast(List[str], d.pop("jobIDs", UNSET))


        run_counter = d.pop("runCounter", UNSET)

        rerun_batch_output = cls(
            batch_id=batch_id,
            job_i_ds=job_i_ds,
            run_counter=run_counter,
        )


        rerun_batch_output.additional_properties = d
        return rerun_batch_output

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
