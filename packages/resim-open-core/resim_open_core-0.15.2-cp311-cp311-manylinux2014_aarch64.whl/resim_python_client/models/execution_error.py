from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from typing import cast
from ..types import UNSET, Unset
from typing import Union

if TYPE_CHECKING:
  from ..models.execution_error_metadata import ExecutionErrorMetadata





T = TypeVar("T", bound="ExecutionError")


@_attrs_define
class ExecutionError:
    """ 
        Attributes:
            error_code (str): Standardized error code (e.g., UNKNOWN_ERROR, NONZERO_EXIT_CODE)
            metadata (Union[Unset, ExecutionErrorMetadata]): Error metadata
     """

    error_code: str
    metadata: Union[Unset, 'ExecutionErrorMetadata'] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.execution_error_metadata import ExecutionErrorMetadata
        error_code = self.error_code

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "errorCode": error_code,
        })
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.execution_error_metadata import ExecutionErrorMetadata
        d = src_dict.copy()
        error_code = d.pop("errorCode")

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, ExecutionErrorMetadata]
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = ExecutionErrorMetadata.from_dict(_metadata)




        execution_error = cls(
            error_code=error_code,
            metadata=metadata,
        )


        execution_error.additional_properties = d
        return execution_error

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
