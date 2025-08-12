from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from typing import cast, Union
from typing import cast

if TYPE_CHECKING:
  from ..models.compare_batch_test_details_type_0 import CompareBatchTestDetailsType0





T = TypeVar("T", bound="CompareBatchTest")


@_attrs_define
class CompareBatchTest:
    """ 
        Attributes:
            experience_id (str):
            experience_name (str):
            from_test (Union['CompareBatchTestDetailsType0', None]):
            to_test (Union['CompareBatchTestDetailsType0', None]):
     """

    experience_id: str
    experience_name: str
    from_test: Union['CompareBatchTestDetailsType0', None]
    to_test: Union['CompareBatchTestDetailsType0', None]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.compare_batch_test_details_type_0 import CompareBatchTestDetailsType0
        experience_id = self.experience_id

        experience_name = self.experience_name

        from_test: Union[Dict[str, Any], None]
        if isinstance(self.from_test, CompareBatchTestDetailsType0):
            from_test = self.from_test.to_dict()
        else:
            from_test = self.from_test

        to_test: Union[Dict[str, Any], None]
        if isinstance(self.to_test, CompareBatchTestDetailsType0):
            to_test = self.to_test.to_dict()
        else:
            to_test = self.to_test


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "experienceID": experience_id,
            "experienceName": experience_name,
            "fromTest": from_test,
            "toTest": to_test,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.compare_batch_test_details_type_0 import CompareBatchTestDetailsType0
        d = src_dict.copy()
        experience_id = d.pop("experienceID")

        experience_name = d.pop("experienceName")

        def _parse_from_test(data: object) -> Union['CompareBatchTestDetailsType0', None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemascompare_batch_test_details_type_0 = CompareBatchTestDetailsType0.from_dict(data)



                return componentsschemascompare_batch_test_details_type_0
            except: # noqa: E722
                pass
            return cast(Union['CompareBatchTestDetailsType0', None], data)

        from_test = _parse_from_test(d.pop("fromTest"))


        def _parse_to_test(data: object) -> Union['CompareBatchTestDetailsType0', None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemascompare_batch_test_details_type_0 = CompareBatchTestDetailsType0.from_dict(data)



                return componentsschemascompare_batch_test_details_type_0
            except: # noqa: E722
                pass
            return cast(Union['CompareBatchTestDetailsType0', None], data)

        to_test = _parse_to_test(d.pop("toTest"))


        compare_batch_test = cls(
            experience_id=experience_id,
            experience_name=experience_name,
            from_test=from_test,
            to_test=to_test,
        )


        compare_batch_test.additional_properties = d
        return compare_batch_test

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
