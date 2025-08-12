from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Union
from ..types import UNSET, Unset






T = TypeVar("T", bound="DebugExperienceOutput")


@_attrs_define
class DebugExperienceOutput:
    """ 
        Attributes:
            batch_id (Union[Unset, str]):
            cluster_ca_data (Union[Unset, str]):
            cluster_endpoint (Union[Unset, str]):
            cluster_token (Union[Unset, str]):
            namespace (Union[Unset, str]):
     """

    batch_id: Union[Unset, str] = UNSET
    cluster_ca_data: Union[Unset, str] = UNSET
    cluster_endpoint: Union[Unset, str] = UNSET
    cluster_token: Union[Unset, str] = UNSET
    namespace: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        batch_id = self.batch_id

        cluster_ca_data = self.cluster_ca_data

        cluster_endpoint = self.cluster_endpoint

        cluster_token = self.cluster_token

        namespace = self.namespace


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batch_id is not UNSET:
            field_dict["batchID"] = batch_id
        if cluster_ca_data is not UNSET:
            field_dict["clusterCAData"] = cluster_ca_data
        if cluster_endpoint is not UNSET:
            field_dict["clusterEndpoint"] = cluster_endpoint
        if cluster_token is not UNSET:
            field_dict["clusterToken"] = cluster_token
        if namespace is not UNSET:
            field_dict["namespace"] = namespace

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        batch_id = d.pop("batchID", UNSET)

        cluster_ca_data = d.pop("clusterCAData", UNSET)

        cluster_endpoint = d.pop("clusterEndpoint", UNSET)

        cluster_token = d.pop("clusterToken", UNSET)

        namespace = d.pop("namespace", UNSET)

        debug_experience_output = cls(
            batch_id=batch_id,
            cluster_ca_data=cluster_ca_data,
            cluster_endpoint=cluster_endpoint,
            cluster_token=cluster_token,
            namespace=namespace,
        )


        debug_experience_output.additional_properties = d
        return debug_experience_output

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
