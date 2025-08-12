from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from typing import cast
from typing import cast, List

if TYPE_CHECKING:
  from ..models.compare_batch_test import CompareBatchTest





T = TypeVar("T", bound="CompareBatchesOutput")


@_attrs_define
class CompareBatchesOutput:
    """ 
        Attributes:
            next_page_token (str):
            tests (List['CompareBatchTest']):
            total (int):
     """

    next_page_token: str
    tests: List['CompareBatchTest']
    total: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.compare_batch_test import CompareBatchTest
        next_page_token = self.next_page_token

        tests = []
        for tests_item_data in self.tests:
            tests_item = tests_item_data.to_dict()
            tests.append(tests_item)



        total = self.total


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "nextPageToken": next_page_token,
            "tests": tests,
            "total": total,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.compare_batch_test import CompareBatchTest
        d = src_dict.copy()
        next_page_token = d.pop("nextPageToken")

        tests = []
        _tests = d.pop("tests")
        for tests_item_data in (_tests):
            tests_item = CompareBatchTest.from_dict(tests_item_data)



            tests.append(tests_item)


        total = d.pop("total")

        compare_batches_output = cls(
            next_page_token=next_page_token,
            tests=tests,
            total=total,
        )


        compare_batches_output.additional_properties = d
        return compare_batches_output

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
