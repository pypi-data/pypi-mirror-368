from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

import datetime
from dateutil.parser import isoparse
from typing import cast
from ..models.parameter_sweep_status import ParameterSweepStatus
from typing import cast, List
from ..types import UNSET, Unset
from typing import Union
from typing import Dict

if TYPE_CHECKING:
  from ..models.parameter_sweep_status_history_type import ParameterSweepStatusHistoryType
  from ..models.sweep_parameter import SweepParameter





T = TypeVar("T", bound="ParameterSweep")


@_attrs_define
class ParameterSweep:
    """ 
        Attributes:
            associated_account (str):
            batches (Union[Unset, List[str]]):
            creation_timestamp (Union[Unset, datetime.datetime]):
            last_updated_timestamp (Union[Unset, datetime.datetime]):
            name (Union[Unset, str]):
            org_id (Union[Unset, str]):
            parameter_sweep_id (Union[Unset, str]):
            parameters (Union[Unset, List['SweepParameter']]):
            project_id (Union[Unset, str]):
            status (Union[Unset, ParameterSweepStatus]):
            status_history (Union[Unset, List['ParameterSweepStatusHistoryType']]):
            user_id (Union[Unset, str]):
     """

    associated_account: str
    batches: Union[Unset, List[str]] = UNSET
    creation_timestamp: Union[Unset, datetime.datetime] = UNSET
    last_updated_timestamp: Union[Unset, datetime.datetime] = UNSET
    name: Union[Unset, str] = UNSET
    org_id: Union[Unset, str] = UNSET
    parameter_sweep_id: Union[Unset, str] = UNSET
    parameters: Union[Unset, List['SweepParameter']] = UNSET
    project_id: Union[Unset, str] = UNSET
    status: Union[Unset, ParameterSweepStatus] = UNSET
    status_history: Union[Unset, List['ParameterSweepStatusHistoryType']] = UNSET
    user_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.parameter_sweep_status_history_type import ParameterSweepStatusHistoryType
        from ..models.sweep_parameter import SweepParameter
        associated_account = self.associated_account

        batches: Union[Unset, List[str]] = UNSET
        if not isinstance(self.batches, Unset):
            batches = self.batches



        creation_timestamp: Union[Unset, str] = UNSET
        if not isinstance(self.creation_timestamp, Unset):
            creation_timestamp = self.creation_timestamp.isoformat()

        last_updated_timestamp: Union[Unset, str] = UNSET
        if not isinstance(self.last_updated_timestamp, Unset):
            last_updated_timestamp = self.last_updated_timestamp.isoformat()

        name = self.name

        org_id = self.org_id

        parameter_sweep_id = self.parameter_sweep_id

        parameters: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = []
            for parameters_item_data in self.parameters:
                parameters_item = parameters_item_data.to_dict()
                parameters.append(parameters_item)



        project_id = self.project_id

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        status_history: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.status_history, Unset):
            status_history = []
            for componentsschemasparameter_sweep_status_history_item_data in self.status_history:
                componentsschemasparameter_sweep_status_history_item = componentsschemasparameter_sweep_status_history_item_data.to_dict()
                status_history.append(componentsschemasparameter_sweep_status_history_item)



        user_id = self.user_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "associatedAccount": associated_account,
        })
        if batches is not UNSET:
            field_dict["batches"] = batches
        if creation_timestamp is not UNSET:
            field_dict["creationTimestamp"] = creation_timestamp
        if last_updated_timestamp is not UNSET:
            field_dict["lastUpdatedTimestamp"] = last_updated_timestamp
        if name is not UNSET:
            field_dict["name"] = name
        if org_id is not UNSET:
            field_dict["orgID"] = org_id
        if parameter_sweep_id is not UNSET:
            field_dict["parameterSweepID"] = parameter_sweep_id
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if project_id is not UNSET:
            field_dict["projectID"] = project_id
        if status is not UNSET:
            field_dict["status"] = status
        if status_history is not UNSET:
            field_dict["statusHistory"] = status_history
        if user_id is not UNSET:
            field_dict["userID"] = user_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.parameter_sweep_status_history_type import ParameterSweepStatusHistoryType
        from ..models.sweep_parameter import SweepParameter
        d = src_dict.copy()
        associated_account = d.pop("associatedAccount")

        batches = cast(List[str], d.pop("batches", UNSET))


        _creation_timestamp = d.pop("creationTimestamp", UNSET)
        creation_timestamp: Union[Unset, datetime.datetime]
        if isinstance(_creation_timestamp,  Unset):
            creation_timestamp = UNSET
        else:
            creation_timestamp = isoparse(_creation_timestamp)




        _last_updated_timestamp = d.pop("lastUpdatedTimestamp", UNSET)
        last_updated_timestamp: Union[Unset, datetime.datetime]
        if isinstance(_last_updated_timestamp,  Unset):
            last_updated_timestamp = UNSET
        else:
            last_updated_timestamp = isoparse(_last_updated_timestamp)




        name = d.pop("name", UNSET)

        org_id = d.pop("orgID", UNSET)

        parameter_sweep_id = d.pop("parameterSweepID", UNSET)

        parameters = []
        _parameters = d.pop("parameters", UNSET)
        for parameters_item_data in (_parameters or []):
            parameters_item = SweepParameter.from_dict(parameters_item_data)



            parameters.append(parameters_item)


        project_id = d.pop("projectID", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, ParameterSweepStatus]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = ParameterSweepStatus(_status)




        status_history = []
        _status_history = d.pop("statusHistory", UNSET)
        for componentsschemasparameter_sweep_status_history_item_data in (_status_history or []):
            componentsschemasparameter_sweep_status_history_item = ParameterSweepStatusHistoryType.from_dict(componentsschemasparameter_sweep_status_history_item_data)



            status_history.append(componentsschemasparameter_sweep_status_history_item)


        user_id = d.pop("userID", UNSET)

        parameter_sweep = cls(
            associated_account=associated_account,
            batches=batches,
            creation_timestamp=creation_timestamp,
            last_updated_timestamp=last_updated_timestamp,
            name=name,
            org_id=org_id,
            parameter_sweep_id=parameter_sweep_id,
            parameters=parameters,
            project_id=project_id,
            status=status,
            status_history=status_history,
            user_id=user_id,
        )


        parameter_sweep.additional_properties = d
        return parameter_sweep

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
