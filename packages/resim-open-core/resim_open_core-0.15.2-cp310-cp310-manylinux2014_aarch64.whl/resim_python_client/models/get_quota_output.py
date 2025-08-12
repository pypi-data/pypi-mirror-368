from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Union
from ..types import UNSET, Unset






T = TypeVar("T", bound="GetQuotaOutput")


@_attrs_define
class GetQuotaOutput:
    """ 
        Attributes:
            available_tokens (Union[Unset, int]):
            max_tokens (Union[Unset, int]):
            org_id (Union[Unset, str]):
            seconds_until_refresh (Union[Unset, int]):
     """

    available_tokens: Union[Unset, int] = UNSET
    max_tokens: Union[Unset, int] = UNSET
    org_id: Union[Unset, str] = UNSET
    seconds_until_refresh: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        available_tokens = self.available_tokens

        max_tokens = self.max_tokens

        org_id = self.org_id

        seconds_until_refresh = self.seconds_until_refresh


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if available_tokens is not UNSET:
            field_dict["availableTokens"] = available_tokens
        if max_tokens is not UNSET:
            field_dict["maxTokens"] = max_tokens
        if org_id is not UNSET:
            field_dict["orgID"] = org_id
        if seconds_until_refresh is not UNSET:
            field_dict["secondsUntilRefresh"] = seconds_until_refresh

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        available_tokens = d.pop("availableTokens", UNSET)

        max_tokens = d.pop("maxTokens", UNSET)

        org_id = d.pop("orgID", UNSET)

        seconds_until_refresh = d.pop("secondsUntilRefresh", UNSET)

        get_quota_output = cls(
            available_tokens=available_tokens,
            max_tokens=max_tokens,
            org_id=org_id,
            seconds_until_refresh=seconds_until_refresh,
        )


        get_quota_output.additional_properties = d
        return get_quota_output

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
