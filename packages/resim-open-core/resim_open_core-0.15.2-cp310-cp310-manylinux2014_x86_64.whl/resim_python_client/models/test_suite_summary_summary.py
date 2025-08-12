from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="TestSuiteSummarySummary")


@_attrs_define
class TestSuiteSummarySummary:
    """ 
        Attributes:
            fixed_tests (int):
            new_issues (int):
            new_tests (int):
     """

    fixed_tests: int
    new_issues: int
    new_tests: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        fixed_tests = self.fixed_tests

        new_issues = self.new_issues

        new_tests = self.new_tests


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "fixedTests": fixed_tests,
            "newIssues": new_issues,
            "newTests": new_tests,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        fixed_tests = d.pop("fixedTests")

        new_issues = d.pop("newIssues")

        new_tests = d.pop("newTests")

        test_suite_summary_summary = cls(
            fixed_tests=fixed_tests,
            new_issues=new_issues,
            new_tests=new_tests,
        )


        test_suite_summary_summary.additional_properties = d
        return test_suite_summary_summary

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
