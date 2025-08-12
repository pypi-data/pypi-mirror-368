from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from typing import cast, List
from typing import cast

if TYPE_CHECKING:
  from ..models.test_suite import TestSuite





T = TypeVar("T", bound="ListTestSuiteOutput")


@_attrs_define
class ListTestSuiteOutput:
    """ 
        Attributes:
            next_page_token (str):
            test_suites (List['TestSuite']):
            total (int):
     """

    next_page_token: str
    test_suites: List['TestSuite']
    total: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.test_suite import TestSuite
        next_page_token = self.next_page_token

        test_suites = []
        for test_suites_item_data in self.test_suites:
            test_suites_item = test_suites_item_data.to_dict()
            test_suites.append(test_suites_item)



        total = self.total


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "nextPageToken": next_page_token,
            "testSuites": test_suites,
            "total": total,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.test_suite import TestSuite
        d = src_dict.copy()
        next_page_token = d.pop("nextPageToken")

        test_suites = []
        _test_suites = d.pop("testSuites")
        for test_suites_item_data in (_test_suites):
            test_suites_item = TestSuite.from_dict(test_suites_item_data)



            test_suites.append(test_suites_item)


        total = d.pop("total")

        list_test_suite_output = cls(
            next_page_token=next_page_token,
            test_suites=test_suites,
            total=total,
        )


        list_test_suite_output.additional_properties = d
        return list_test_suite_output

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
