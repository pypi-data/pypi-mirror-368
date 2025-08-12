from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
from typing import Union
from typing import cast
from ..types import UNSET, Unset
from typing import Dict

if TYPE_CHECKING:
  from ..models.batch import Batch





T = TypeVar("T", bound="ListBatchesOutput")


@_attrs_define
class ListBatchesOutput:
    """ 
        Attributes:
            batches (Union[Unset, List['Batch']]):
            next_page_token (Union[Unset, str]):
            total (Union[Unset, int]):
     """

    batches: Union[Unset, List['Batch']] = UNSET
    next_page_token: Union[Unset, str] = UNSET
    total: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.batch import Batch
        batches: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.batches, Unset):
            batches = []
            for batches_item_data in self.batches:
                batches_item = batches_item_data.to_dict()
                batches.append(batches_item)



        next_page_token = self.next_page_token

        total = self.total


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batches is not UNSET:
            field_dict["batches"] = batches
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.batch import Batch
        d = src_dict.copy()
        batches = []
        _batches = d.pop("batches", UNSET)
        for batches_item_data in (_batches or []):
            batches_item = Batch.from_dict(batches_item_data)



            batches.append(batches_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        total = d.pop("total", UNSET)

        list_batches_output = cls(
            batches=batches,
            next_page_token=next_page_token,
            total=total,
        )


        list_batches_output.additional_properties = d
        return list_batches_output

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
