from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.test_suite_summary import TestSuiteSummary





T = TypeVar("T", bound="TestSuiteSummaryOutput")


@_attrs_define
class TestSuiteSummaryOutput:
    """ 
        Attributes:
            next_page_token (str):
            test_suites (List['TestSuiteSummary']):
     """

    next_page_token: str
    test_suites: List['TestSuiteSummary']
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.test_suite_summary import TestSuiteSummary
        next_page_token = self.next_page_token

        test_suites = []
        for test_suites_item_data in self.test_suites:
            test_suites_item = test_suites_item_data.to_dict()
            test_suites.append(test_suites_item)




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "nextPageToken": next_page_token,
            "testSuites": test_suites,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.test_suite_summary import TestSuiteSummary
        d = src_dict.copy()
        next_page_token = d.pop("nextPageToken")

        test_suites = []
        _test_suites = d.pop("testSuites")
        for test_suites_item_data in (_test_suites):
            test_suites_item = TestSuiteSummary.from_dict(test_suites_item_data)



            test_suites.append(test_suites_item)


        test_suite_summary_output = cls(
            next_page_token=next_page_token,
            test_suites=test_suites,
        )


        test_suite_summary_output.additional_properties = d
        return test_suite_summary_output

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
