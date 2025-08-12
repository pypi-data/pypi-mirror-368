from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from ..types import UNSET, Unset
from typing import cast, Union
from typing import cast
from typing import cast, List
from typing import Union

if TYPE_CHECKING:
  from ..models.key_metric_type_0 import KeyMetricType0
  from ..models.test_suite_summary_summary import TestSuiteSummarySummary
  from ..models.test_suite_batch_summary_job_results import TestSuiteBatchSummaryJobResults
  from ..models.reference_batch_summary_type_0 import ReferenceBatchSummaryType0





T = TypeVar("T", bound="TestSuiteSummary")


@_attrs_define
class TestSuiteSummary:
    """ 
        Attributes:
            batches (List['TestSuiteBatchSummaryJobResults']):
            branch_id (str):
            key_metric (Union['KeyMetricType0', None]):
            name (str):
            project_id (str):
            reference_batch_summary (Union['ReferenceBatchSummaryType0', None]):
            report_id (str):
            summary (TestSuiteSummarySummary):
            system_id (str):
            test_suite_description (str):
            test_suite_id (str):
            test_suite_revision (int):
            reference_batch (Union[Unset, TestSuiteBatchSummaryJobResults]):
     """

    batches: List['TestSuiteBatchSummaryJobResults']
    branch_id: str
    key_metric: Union['KeyMetricType0', None]
    name: str
    project_id: str
    reference_batch_summary: Union['ReferenceBatchSummaryType0', None]
    report_id: str
    summary: 'TestSuiteSummarySummary'
    system_id: str
    test_suite_description: str
    test_suite_id: str
    test_suite_revision: int
    reference_batch: Union[Unset, 'TestSuiteBatchSummaryJobResults'] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.key_metric_type_0 import KeyMetricType0
        from ..models.test_suite_summary_summary import TestSuiteSummarySummary
        from ..models.test_suite_batch_summary_job_results import TestSuiteBatchSummaryJobResults
        from ..models.reference_batch_summary_type_0 import ReferenceBatchSummaryType0
        batches = []
        for batches_item_data in self.batches:
            batches_item = batches_item_data.to_dict()
            batches.append(batches_item)



        branch_id = self.branch_id

        key_metric: Union[Dict[str, Any], None]
        if isinstance(self.key_metric, KeyMetricType0):
            key_metric = self.key_metric.to_dict()
        else:
            key_metric = self.key_metric

        name = self.name

        project_id = self.project_id

        reference_batch_summary: Union[Dict[str, Any], None]
        if isinstance(self.reference_batch_summary, ReferenceBatchSummaryType0):
            reference_batch_summary = self.reference_batch_summary.to_dict()
        else:
            reference_batch_summary = self.reference_batch_summary

        report_id = self.report_id

        summary = self.summary.to_dict()

        system_id = self.system_id

        test_suite_description = self.test_suite_description

        test_suite_id = self.test_suite_id

        test_suite_revision = self.test_suite_revision

        reference_batch: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.reference_batch, Unset):
            reference_batch = self.reference_batch.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "batches": batches,
            "branchID": branch_id,
            "keyMetric": key_metric,
            "name": name,
            "projectID": project_id,
            "referenceBatchSummary": reference_batch_summary,
            "reportID": report_id,
            "summary": summary,
            "systemID": system_id,
            "testSuiteDescription": test_suite_description,
            "testSuiteID": test_suite_id,
            "testSuiteRevision": test_suite_revision,
        })
        if reference_batch is not UNSET:
            field_dict["referenceBatch"] = reference_batch

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.key_metric_type_0 import KeyMetricType0
        from ..models.test_suite_summary_summary import TestSuiteSummarySummary
        from ..models.test_suite_batch_summary_job_results import TestSuiteBatchSummaryJobResults
        from ..models.reference_batch_summary_type_0 import ReferenceBatchSummaryType0
        d = src_dict.copy()
        batches = []
        _batches = d.pop("batches")
        for batches_item_data in (_batches):
            batches_item = TestSuiteBatchSummaryJobResults.from_dict(batches_item_data)



            batches.append(batches_item)


        branch_id = d.pop("branchID")

        def _parse_key_metric(data: object) -> Union['KeyMetricType0', None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemaskey_metric_type_0 = KeyMetricType0.from_dict(data)



                return componentsschemaskey_metric_type_0
            except: # noqa: E722
                pass
            return cast(Union['KeyMetricType0', None], data)

        key_metric = _parse_key_metric(d.pop("keyMetric"))


        name = d.pop("name")

        project_id = d.pop("projectID")

        def _parse_reference_batch_summary(data: object) -> Union['ReferenceBatchSummaryType0', None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasreference_batch_summary_type_0 = ReferenceBatchSummaryType0.from_dict(data)



                return componentsschemasreference_batch_summary_type_0
            except: # noqa: E722
                pass
            return cast(Union['ReferenceBatchSummaryType0', None], data)

        reference_batch_summary = _parse_reference_batch_summary(d.pop("referenceBatchSummary"))


        report_id = d.pop("reportID")

        summary = TestSuiteSummarySummary.from_dict(d.pop("summary"))




        system_id = d.pop("systemID")

        test_suite_description = d.pop("testSuiteDescription")

        test_suite_id = d.pop("testSuiteID")

        test_suite_revision = d.pop("testSuiteRevision")

        _reference_batch = d.pop("referenceBatch", UNSET)
        reference_batch: Union[Unset, TestSuiteBatchSummaryJobResults]
        if isinstance(_reference_batch,  Unset):
            reference_batch = UNSET
        else:
            reference_batch = TestSuiteBatchSummaryJobResults.from_dict(_reference_batch)




        test_suite_summary = cls(
            batches=batches,
            branch_id=branch_id,
            key_metric=key_metric,
            name=name,
            project_id=project_id,
            reference_batch_summary=reference_batch_summary,
            report_id=report_id,
            summary=summary,
            system_id=system_id,
            test_suite_description=test_suite_description,
            test_suite_id=test_suite_id,
            test_suite_revision=test_suite_revision,
            reference_batch=reference_batch,
        )


        test_suite_summary.additional_properties = d
        return test_suite_summary

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
