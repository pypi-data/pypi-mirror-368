from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union
from ..models.object_type import ObjectType






T = TypeVar("T", bound="ViewMetadata")


@_attrs_define
class ViewMetadata:
    """ 
        Attributes:
            file_name (Union[Unset, str]):
            line_number (Union[Unset, int]):
            object_name (Union[Unset, str]):
            object_type (Union[Unset, ObjectType]):
     """

    file_name: Union[Unset, str] = UNSET
    line_number: Union[Unset, int] = UNSET
    object_name: Union[Unset, str] = UNSET
    object_type: Union[Unset, ObjectType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        file_name = self.file_name

        line_number = self.line_number

        object_name = self.object_name

        object_type: Union[Unset, str] = UNSET
        if not isinstance(self.object_type, Unset):
            object_type = self.object_type.value



        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if file_name is not UNSET:
            field_dict["fileName"] = file_name
        if line_number is not UNSET:
            field_dict["lineNumber"] = line_number
        if object_name is not UNSET:
            field_dict["objectName"] = object_name
        if object_type is not UNSET:
            field_dict["objectType"] = object_type

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        file_name = d.pop("fileName", UNSET)

        line_number = d.pop("lineNumber", UNSET)

        object_name = d.pop("objectName", UNSET)

        _object_type = d.pop("objectType", UNSET)
        object_type: Union[Unset, ObjectType]
        if isinstance(_object_type,  Unset):
            object_type = UNSET
        else:
            object_type = ObjectType(_object_type)




        view_metadata = cls(
            file_name=file_name,
            line_number=line_number,
            object_name=object_name,
            object_type=object_type,
        )


        view_metadata.additional_properties = d
        return view_metadata

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
