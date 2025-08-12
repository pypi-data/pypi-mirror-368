from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union
from typing import cast, List






T = TypeVar("T", bound="ListJobEventTagsOutput")


@_attrs_define
class ListJobEventTagsOutput:
    """ 
        Attributes:
            event_tags (Union[Unset, List[str]]):
            next_page_token (Union[Unset, str]):
     """

    event_tags: Union[Unset, List[str]] = UNSET
    next_page_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        event_tags: Union[Unset, List[str]] = UNSET
        if not isinstance(self.event_tags, Unset):
            event_tags = self.event_tags



        next_page_token = self.next_page_token


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if event_tags is not UNSET:
            field_dict["eventTags"] = event_tags
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        event_tags = cast(List[str], d.pop("eventTags", UNSET))


        next_page_token = d.pop("nextPageToken", UNSET)

        list_job_event_tags_output = cls(
            event_tags=event_tags,
            next_page_token=next_page_token,
        )


        list_job_event_tags_output.additional_properties = d
        return list_job_event_tags_output

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
