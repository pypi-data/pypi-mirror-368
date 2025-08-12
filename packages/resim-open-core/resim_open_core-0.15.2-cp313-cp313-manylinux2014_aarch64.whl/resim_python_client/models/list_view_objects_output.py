from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import cast, List
from ..types import UNSET, Unset
from typing import Union
from typing import Dict

if TYPE_CHECKING:
  from ..models.view_object import ViewObject





T = TypeVar("T", bound="ListViewObjectsOutput")


@_attrs_define
class ListViewObjectsOutput:
    """ 
        Attributes:
            next_page_token (Union[Unset, str]):
            view_sessions (Union[Unset, List['ViewObject']]):
     """

    next_page_token: Union[Unset, str] = UNSET
    view_sessions: Union[Unset, List['ViewObject']] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.view_object import ViewObject
        next_page_token = self.next_page_token

        view_sessions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.view_sessions, Unset):
            view_sessions = []
            for view_sessions_item_data in self.view_sessions:
                view_sessions_item = view_sessions_item_data.to_dict()
                view_sessions.append(view_sessions_item)




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if view_sessions is not UNSET:
            field_dict["viewSessions"] = view_sessions

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.view_object import ViewObject
        d = src_dict.copy()
        next_page_token = d.pop("nextPageToken", UNSET)

        view_sessions = []
        _view_sessions = d.pop("viewSessions", UNSET)
        for view_sessions_item_data in (_view_sessions or []):
            view_sessions_item = ViewObject.from_dict(view_sessions_item_data)



            view_sessions.append(view_sessions_item)


        list_view_objects_output = cls(
            next_page_token=next_page_token,
            view_sessions=view_sessions,
        )


        list_view_objects_output.additional_properties = d
        return list_view_objects_output

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
