from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from typing import cast, Union
from typing import cast

if TYPE_CHECKING:
  from ..models.batch import Batch





T = TypeVar("T", bound="BatchSuggestionsOutput")


@_attrs_define
class BatchSuggestionsOutput:
    """ 
        Attributes:
            last_passing_on_branch (Union['Batch', None]):
            last_passing_on_main (Union['Batch', None]):
            latest_on_branch (Union['Batch', None]):
            latest_on_main (Union['Batch', None]):
     """

    last_passing_on_branch: Union['Batch', None]
    last_passing_on_main: Union['Batch', None]
    latest_on_branch: Union['Batch', None]
    latest_on_main: Union['Batch', None]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.batch import Batch
        last_passing_on_branch: Union[Dict[str, Any], None]
        if isinstance(self.last_passing_on_branch, Batch):
            last_passing_on_branch = self.last_passing_on_branch.to_dict()
        else:
            last_passing_on_branch = self.last_passing_on_branch

        last_passing_on_main: Union[Dict[str, Any], None]
        if isinstance(self.last_passing_on_main, Batch):
            last_passing_on_main = self.last_passing_on_main.to_dict()
        else:
            last_passing_on_main = self.last_passing_on_main

        latest_on_branch: Union[Dict[str, Any], None]
        if isinstance(self.latest_on_branch, Batch):
            latest_on_branch = self.latest_on_branch.to_dict()
        else:
            latest_on_branch = self.latest_on_branch

        latest_on_main: Union[Dict[str, Any], None]
        if isinstance(self.latest_on_main, Batch):
            latest_on_main = self.latest_on_main.to_dict()
        else:
            latest_on_main = self.latest_on_main


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "lastPassingOnBranch": last_passing_on_branch,
            "lastPassingOnMain": last_passing_on_main,
            "latestOnBranch": latest_on_branch,
            "latestOnMain": latest_on_main,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.batch import Batch
        d = src_dict.copy()
        def _parse_last_passing_on_branch(data: object) -> Union['Batch', None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                last_passing_on_branch_type_1 = Batch.from_dict(data)



                return last_passing_on_branch_type_1
            except: # noqa: E722
                pass
            return cast(Union['Batch', None], data)

        last_passing_on_branch = _parse_last_passing_on_branch(d.pop("lastPassingOnBranch"))


        def _parse_last_passing_on_main(data: object) -> Union['Batch', None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                last_passing_on_main_type_1 = Batch.from_dict(data)



                return last_passing_on_main_type_1
            except: # noqa: E722
                pass
            return cast(Union['Batch', None], data)

        last_passing_on_main = _parse_last_passing_on_main(d.pop("lastPassingOnMain"))


        def _parse_latest_on_branch(data: object) -> Union['Batch', None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                latest_on_branch_type_1 = Batch.from_dict(data)



                return latest_on_branch_type_1
            except: # noqa: E722
                pass
            return cast(Union['Batch', None], data)

        latest_on_branch = _parse_latest_on_branch(d.pop("latestOnBranch"))


        def _parse_latest_on_main(data: object) -> Union['Batch', None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                latest_on_main_type_1 = Batch.from_dict(data)



                return latest_on_main_type_1
            except: # noqa: E722
                pass
            return cast(Union['Batch', None], data)

        latest_on_main = _parse_latest_on_main(d.pop("latestOnMain"))


        batch_suggestions_output = cls(
            last_passing_on_branch=last_passing_on_branch,
            last_passing_on_main=last_passing_on_main,
            latest_on_branch=latest_on_branch,
            latest_on_main=latest_on_main,
        )


        batch_suggestions_output.additional_properties = d
        return batch_suggestions_output

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
