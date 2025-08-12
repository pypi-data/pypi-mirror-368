from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.triggered_via import TriggeredVia
from typing import Union
from typing import cast, List
from ..types import UNSET, Unset
from typing import cast, Union
from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.batch_parameters import BatchParameters
  from ..models.experience_filter_input import ExperienceFilterInput





T = TypeVar("T", bound="BatchInput")


@_attrs_define
class BatchInput:
    """ 
        Attributes:
            allowable_failure_percent (Union[None, Unset, int]):
            associated_account (Union[Unset, str]):
            batch_name (Union[Unset, str]):
            build_id (Union[Unset, str]):
            excluded_experience_i_ds (Union[List[str], None, Unset]):
            experience_i_ds (Union[List[str], None, Unset]):
            experience_names (Union[List[str], None, Unset]):
            experience_tag_i_ds (Union[List[str], None, Unset]):
            experience_tag_names (Union[List[str], None, Unset]):
            filters (Union[Unset, ExperienceFilterInput]):
            metrics_build_id (Union[Unset, str]):
            metrics_set_name (Union[None, Unset, str]):
            parameters (Union[Unset, BatchParameters]):
            pool_labels (Union[Unset, List[str]]):
            triggered_via (Union[Unset, TriggeredVia]):
     """

    allowable_failure_percent: Union[None, Unset, int] = UNSET
    associated_account: Union[Unset, str] = UNSET
    batch_name: Union[Unset, str] = UNSET
    build_id: Union[Unset, str] = UNSET
    excluded_experience_i_ds: Union[List[str], None, Unset] = UNSET
    experience_i_ds: Union[List[str], None, Unset] = UNSET
    experience_names: Union[List[str], None, Unset] = UNSET
    experience_tag_i_ds: Union[List[str], None, Unset] = UNSET
    experience_tag_names: Union[List[str], None, Unset] = UNSET
    filters: Union[Unset, 'ExperienceFilterInput'] = UNSET
    metrics_build_id: Union[Unset, str] = UNSET
    metrics_set_name: Union[None, Unset, str] = UNSET
    parameters: Union[Unset, 'BatchParameters'] = UNSET
    pool_labels: Union[Unset, List[str]] = UNSET
    triggered_via: Union[Unset, TriggeredVia] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.batch_parameters import BatchParameters
        from ..models.experience_filter_input import ExperienceFilterInput
        allowable_failure_percent: Union[None, Unset, int]
        if isinstance(self.allowable_failure_percent, Unset):
            allowable_failure_percent = UNSET
        else:
            allowable_failure_percent = self.allowable_failure_percent

        associated_account = self.associated_account

        batch_name = self.batch_name

        build_id = self.build_id

        excluded_experience_i_ds: Union[List[str], None, Unset]
        if isinstance(self.excluded_experience_i_ds, Unset):
            excluded_experience_i_ds = UNSET
        elif isinstance(self.excluded_experience_i_ds, list):
            excluded_experience_i_ds = self.excluded_experience_i_ds


        else:
            excluded_experience_i_ds = self.excluded_experience_i_ds

        experience_i_ds: Union[List[str], None, Unset]
        if isinstance(self.experience_i_ds, Unset):
            experience_i_ds = UNSET
        elif isinstance(self.experience_i_ds, list):
            experience_i_ds = self.experience_i_ds


        else:
            experience_i_ds = self.experience_i_ds

        experience_names: Union[List[str], None, Unset]
        if isinstance(self.experience_names, Unset):
            experience_names = UNSET
        elif isinstance(self.experience_names, list):
            experience_names = self.experience_names


        else:
            experience_names = self.experience_names

        experience_tag_i_ds: Union[List[str], None, Unset]
        if isinstance(self.experience_tag_i_ds, Unset):
            experience_tag_i_ds = UNSET
        elif isinstance(self.experience_tag_i_ds, list):
            experience_tag_i_ds = self.experience_tag_i_ds


        else:
            experience_tag_i_ds = self.experience_tag_i_ds

        experience_tag_names: Union[List[str], None, Unset]
        if isinstance(self.experience_tag_names, Unset):
            experience_tag_names = UNSET
        elif isinstance(self.experience_tag_names, list):
            experience_tag_names = self.experience_tag_names


        else:
            experience_tag_names = self.experience_tag_names

        filters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()

        metrics_build_id = self.metrics_build_id

        metrics_set_name: Union[None, Unset, str]
        if isinstance(self.metrics_set_name, Unset):
            metrics_set_name = UNSET
        else:
            metrics_set_name = self.metrics_set_name

        parameters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        pool_labels: Union[Unset, List[str]] = UNSET
        if not isinstance(self.pool_labels, Unset):
            pool_labels = self.pool_labels



        triggered_via: Union[Unset, str] = UNSET
        if not isinstance(self.triggered_via, Unset):
            triggered_via = self.triggered_via.value



        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if allowable_failure_percent is not UNSET:
            field_dict["allowableFailurePercent"] = allowable_failure_percent
        if associated_account is not UNSET:
            field_dict["associatedAccount"] = associated_account
        if batch_name is not UNSET:
            field_dict["batchName"] = batch_name
        if build_id is not UNSET:
            field_dict["buildID"] = build_id
        if excluded_experience_i_ds is not UNSET:
            field_dict["excludedExperienceIDs"] = excluded_experience_i_ds
        if experience_i_ds is not UNSET:
            field_dict["experienceIDs"] = experience_i_ds
        if experience_names is not UNSET:
            field_dict["experienceNames"] = experience_names
        if experience_tag_i_ds is not UNSET:
            field_dict["experienceTagIDs"] = experience_tag_i_ds
        if experience_tag_names is not UNSET:
            field_dict["experienceTagNames"] = experience_tag_names
        if filters is not UNSET:
            field_dict["filters"] = filters
        if metrics_build_id is not UNSET:
            field_dict["metricsBuildID"] = metrics_build_id
        if metrics_set_name is not UNSET:
            field_dict["metricsSetName"] = metrics_set_name
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if pool_labels is not UNSET:
            field_dict["poolLabels"] = pool_labels
        if triggered_via is not UNSET:
            field_dict["triggeredVia"] = triggered_via

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.batch_parameters import BatchParameters
        from ..models.experience_filter_input import ExperienceFilterInput
        d = src_dict.copy()
        def _parse_allowable_failure_percent(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        allowable_failure_percent = _parse_allowable_failure_percent(d.pop("allowableFailurePercent", UNSET))


        associated_account = d.pop("associatedAccount", UNSET)

        batch_name = d.pop("batchName", UNSET)

        build_id = d.pop("buildID", UNSET)

        def _parse_excluded_experience_i_ds(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                excluded_experience_i_ds_type_0 = cast(List[str], data)

                return excluded_experience_i_ds_type_0
            except: # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        excluded_experience_i_ds = _parse_excluded_experience_i_ds(d.pop("excludedExperienceIDs", UNSET))


        def _parse_experience_i_ds(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                experience_i_ds_type_0 = cast(List[str], data)

                return experience_i_ds_type_0
            except: # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        experience_i_ds = _parse_experience_i_ds(d.pop("experienceIDs", UNSET))


        def _parse_experience_names(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                experience_names_type_0 = cast(List[str], data)

                return experience_names_type_0
            except: # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        experience_names = _parse_experience_names(d.pop("experienceNames", UNSET))


        def _parse_experience_tag_i_ds(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                experience_tag_i_ds_type_0 = cast(List[str], data)

                return experience_tag_i_ds_type_0
            except: # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        experience_tag_i_ds = _parse_experience_tag_i_ds(d.pop("experienceTagIDs", UNSET))


        def _parse_experience_tag_names(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                experience_tag_names_type_0 = cast(List[str], data)

                return experience_tag_names_type_0
            except: # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        experience_tag_names = _parse_experience_tag_names(d.pop("experienceTagNames", UNSET))


        _filters = d.pop("filters", UNSET)
        filters: Union[Unset, ExperienceFilterInput]
        if isinstance(_filters,  Unset):
            filters = UNSET
        else:
            filters = ExperienceFilterInput.from_dict(_filters)




        metrics_build_id = d.pop("metricsBuildID", UNSET)

        def _parse_metrics_set_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        metrics_set_name = _parse_metrics_set_name(d.pop("metricsSetName", UNSET))


        _parameters = d.pop("parameters", UNSET)
        parameters: Union[Unset, BatchParameters]
        if isinstance(_parameters,  Unset):
            parameters = UNSET
        else:
            parameters = BatchParameters.from_dict(_parameters)




        pool_labels = cast(List[str], d.pop("poolLabels", UNSET))


        _triggered_via = d.pop("triggeredVia", UNSET)
        triggered_via: Union[Unset, TriggeredVia]
        if isinstance(_triggered_via,  Unset):
            triggered_via = UNSET
        else:
            triggered_via = TriggeredVia(_triggered_via)




        batch_input = cls(
            allowable_failure_percent=allowable_failure_percent,
            associated_account=associated_account,
            batch_name=batch_name,
            build_id=build_id,
            excluded_experience_i_ds=excluded_experience_i_ds,
            experience_i_ds=experience_i_ds,
            experience_names=experience_names,
            experience_tag_i_ds=experience_tag_i_ds,
            experience_tag_names=experience_tag_names,
            filters=filters,
            metrics_build_id=metrics_build_id,
            metrics_set_name=metrics_set_name,
            parameters=parameters,
            pool_labels=pool_labels,
            triggered_via=triggered_via,
        )


        batch_input.additional_properties = d
        return batch_input

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
