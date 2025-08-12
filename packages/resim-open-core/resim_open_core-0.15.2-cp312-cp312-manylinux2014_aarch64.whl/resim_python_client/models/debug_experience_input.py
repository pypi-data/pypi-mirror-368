from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Union
from ..types import UNSET, Unset
from typing import cast, List






T = TypeVar("T", bound="DebugExperienceInput")


@_attrs_define
class DebugExperienceInput:
    """ 
        Attributes:
            batch_id (Union[Unset, str]):
            build_id (Union[Unset, str]):
            pool_labels (Union[Unset, List[str]]):
            test_suite_id (Union[Unset, str]):
     """

    batch_id: Union[Unset, str] = UNSET
    build_id: Union[Unset, str] = UNSET
    pool_labels: Union[Unset, List[str]] = UNSET
    test_suite_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        batch_id = self.batch_id

        build_id = self.build_id

        pool_labels: Union[Unset, List[str]] = UNSET
        if not isinstance(self.pool_labels, Unset):
            pool_labels = self.pool_labels



        test_suite_id = self.test_suite_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batch_id is not UNSET:
            field_dict["batchID"] = batch_id
        if build_id is not UNSET:
            field_dict["buildID"] = build_id
        if pool_labels is not UNSET:
            field_dict["poolLabels"] = pool_labels
        if test_suite_id is not UNSET:
            field_dict["testSuiteID"] = test_suite_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        batch_id = d.pop("batchID", UNSET)

        build_id = d.pop("buildID", UNSET)

        pool_labels = cast(List[str], d.pop("poolLabels", UNSET))


        test_suite_id = d.pop("testSuiteID", UNSET)

        debug_experience_input = cls(
            batch_id=batch_id,
            build_id=build_id,
            pool_labels=pool_labels,
            test_suite_id=test_suite_id,
        )


        debug_experience_input.additional_properties = d
        return debug_experience_input

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
