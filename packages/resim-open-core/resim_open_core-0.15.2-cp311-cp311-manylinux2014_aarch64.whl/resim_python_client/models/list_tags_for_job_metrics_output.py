from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from ..types import UNSET, Unset
from typing import cast
from typing import cast, List
from typing import Union

if TYPE_CHECKING:
  from ..models.metric_tag import MetricTag





T = TypeVar("T", bound="ListTagsForJobMetricsOutput")


@_attrs_define
class ListTagsForJobMetricsOutput:
    """ 
        Attributes:
            next_page_token (Union[Unset, str]):
            tags (Union[Unset, List['MetricTag']]):
     """

    next_page_token: Union[Unset, str] = UNSET
    tags: Union[Unset, List['MetricTag']] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.metric_tag import MetricTag
        next_page_token = self.next_page_token

        tags: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()
                tags.append(tags_item)




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.metric_tag import MetricTag
        d = src_dict.copy()
        next_page_token = d.pop("nextPageToken", UNSET)

        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in (_tags or []):
            tags_item = MetricTag.from_dict(tags_item_data)



            tags.append(tags_item)


        list_tags_for_job_metrics_output = cls(
            next_page_token=next_page_token,
            tags=tags,
        )


        list_tags_for_job_metrics_output.additional_properties = d
        return list_tags_for_job_metrics_output

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
