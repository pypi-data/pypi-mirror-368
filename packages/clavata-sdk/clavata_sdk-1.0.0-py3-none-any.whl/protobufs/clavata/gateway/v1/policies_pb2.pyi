from clavata.shared.v1 import public_pb2 as _public_pb2
from clavata.shared.v1 import shared_pb2 as _shared_pb2
from clavata.gateway.v1 import errs_pb2 as _errs_pb2
from google.api import visibility_pb2 as _visibility_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GeneratePolicyTaskStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[GeneratePolicyTaskStatus]
    PENDING: _ClassVar[GeneratePolicyTaskStatus]
    RUNNING: _ClassVar[GeneratePolicyTaskStatus]
    COMPLETED: _ClassVar[GeneratePolicyTaskStatus]
    FAILED: _ClassVar[GeneratePolicyTaskStatus]
    CANCELLED: _ClassVar[GeneratePolicyTaskStatus]
UNSPECIFIED: GeneratePolicyTaskStatus
PENDING: GeneratePolicyTaskStatus
RUNNING: GeneratePolicyTaskStatus
COMPLETED: GeneratePolicyTaskStatus
FAILED: GeneratePolicyTaskStatus
CANCELLED: GeneratePolicyTaskStatus

class PolicyQuery(_message.Message):
    __slots__ = ("uuids", "keys", "include_expunged", "created_time_range", "updated_time_range")
    UUIDS_FIELD_NUMBER: _ClassVar[int]
    KEYS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_EXPUNGED_FIELD_NUMBER: _ClassVar[int]
    CREATED_TIME_RANGE_FIELD_NUMBER: _ClassVar[int]
    UPDATED_TIME_RANGE_FIELD_NUMBER: _ClassVar[int]
    uuids: _containers.RepeatedScalarFieldContainer[str]
    keys: _containers.RepeatedScalarFieldContainer[str]
    include_expunged: bool
    created_time_range: _public_pb2.TimeRange
    updated_time_range: _public_pb2.TimeRange
    def __init__(self, uuids: _Optional[_Iterable[str]] = ..., keys: _Optional[_Iterable[str]] = ..., include_expunged: bool = ..., created_time_range: _Optional[_Union[_public_pb2.TimeRange, _Mapping]] = ..., updated_time_range: _Optional[_Union[_public_pb2.TimeRange, _Mapping]] = ...) -> None: ...

class PolicyVersionQuery(_message.Message):
    __slots__ = ("policy_identifier", "version_uuids", "include_expunged", "created_time_range")
    POLICY_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    VERSION_UUIDS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_EXPUNGED_FIELD_NUMBER: _ClassVar[int]
    CREATED_TIME_RANGE_FIELD_NUMBER: _ClassVar[int]
    policy_identifier: _shared_pb2.PolicyIdentifier
    version_uuids: _containers.RepeatedScalarFieldContainer[str]
    include_expunged: bool
    created_time_range: _public_pb2.TimeRange
    def __init__(self, policy_identifier: _Optional[_Union[_shared_pb2.PolicyIdentifier, _Mapping]] = ..., version_uuids: _Optional[_Iterable[str]] = ..., include_expunged: bool = ..., created_time_range: _Optional[_Union[_public_pb2.TimeRange, _Mapping]] = ...) -> None: ...

class GetPolicyRequest(_message.Message):
    __slots__ = ("policy_id",)
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    policy_id: str
    def __init__(self, policy_id: _Optional[str] = ...) -> None: ...

class GetPolicyResponse(_message.Message):
    __slots__ = ("policy",)
    POLICY_FIELD_NUMBER: _ClassVar[int]
    policy: _shared_pb2.Policy
    def __init__(self, policy: _Optional[_Union[_shared_pb2.Policy, _Mapping]] = ...) -> None: ...

class GetPoliciesRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: PolicyQuery
    def __init__(self, query: _Optional[_Union[PolicyQuery, _Mapping]] = ...) -> None: ...

class GetPoliciesResponse(_message.Message):
    __slots__ = ("policies",)
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    policies: _containers.RepeatedCompositeFieldContainer[_shared_pb2.Policy]
    def __init__(self, policies: _Optional[_Iterable[_Union[_shared_pb2.Policy, _Mapping]]] = ...) -> None: ...

class UpdatePolicyRequest(_message.Message):
    __slots__ = ("identifier", "policy_key", "disabled", "dataset_id")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    identifier: _shared_pb2.PolicyIdentifier
    policy_key: str
    disabled: bool
    dataset_id: str
    def __init__(self, identifier: _Optional[_Union[_shared_pb2.PolicyIdentifier, _Mapping]] = ..., policy_key: _Optional[str] = ..., disabled: bool = ..., dataset_id: _Optional[str] = ...) -> None: ...

class UpdatePolicyResponse(_message.Message):
    __slots__ = ("policy",)
    POLICY_FIELD_NUMBER: _ClassVar[int]
    policy: _shared_pb2.Policy
    def __init__(self, policy: _Optional[_Union[_shared_pb2.Policy, _Mapping]] = ...) -> None: ...

class GetPolicyVersionsRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: PolicyVersionQuery
    def __init__(self, query: _Optional[_Union[PolicyVersionQuery, _Mapping]] = ...) -> None: ...

class GetPolicyVersionsResponse(_message.Message):
    __slots__ = ("policy_versions",)
    POLICY_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    policy_versions: _containers.RepeatedCompositeFieldContainer[_shared_pb2.PolicyVersion]
    def __init__(self, policy_versions: _Optional[_Iterable[_Union[_shared_pb2.PolicyVersion, _Mapping]]] = ...) -> None: ...

class GetActivePolicyVersionsRequest(_message.Message):
    __slots__ = ("policy_identifiers",)
    POLICY_IDENTIFIERS_FIELD_NUMBER: _ClassVar[int]
    policy_identifiers: _containers.RepeatedCompositeFieldContainer[_shared_pb2.PolicyIdentifier]
    def __init__(self, policy_identifiers: _Optional[_Iterable[_Union[_shared_pb2.PolicyIdentifier, _Mapping]]] = ...) -> None: ...

class GetActivePolicyVersionsResponse(_message.Message):
    __slots__ = ("policy_versions",)
    POLICY_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    policy_versions: _containers.RepeatedCompositeFieldContainer[_shared_pb2.PolicyVersion]
    def __init__(self, policy_versions: _Optional[_Iterable[_Union[_shared_pb2.PolicyVersion, _Mapping]]] = ...) -> None: ...

class DeletePolicyRequest(_message.Message):
    __slots__ = ("policy_identifier",)
    POLICY_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    policy_identifier: _shared_pb2.PolicyIdentifier
    def __init__(self, policy_identifier: _Optional[_Union[_shared_pb2.PolicyIdentifier, _Mapping]] = ...) -> None: ...

class DeletePolicyResponse(_message.Message):
    __slots__ = ("policy_id", "policy_key", "deleted")
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    policy_id: str
    policy_key: str
    deleted: bool
    def __init__(self, policy_id: _Optional[str] = ..., policy_key: _Optional[str] = ..., deleted: bool = ...) -> None: ...

class UndeletePolicyRequest(_message.Message):
    __slots__ = ("policy_identifier",)
    POLICY_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    policy_identifier: _shared_pb2.PolicyIdentifier
    def __init__(self, policy_identifier: _Optional[_Union[_shared_pb2.PolicyIdentifier, _Mapping]] = ...) -> None: ...

class UndeletePolicyResponse(_message.Message):
    __slots__ = ("policy_id", "policy_key", "deleted")
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    policy_id: str
    policy_key: str
    deleted: bool
    def __init__(self, policy_id: _Optional[str] = ..., policy_key: _Optional[str] = ..., deleted: bool = ...) -> None: ...

class SetActivePolicyVersionRequest(_message.Message):
    __slots__ = ("policy_identifier", "active_version_id")
    POLICY_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    policy_identifier: _shared_pb2.PolicyIdentifier
    active_version_id: str
    def __init__(self, policy_identifier: _Optional[_Union[_shared_pb2.PolicyIdentifier, _Mapping]] = ..., active_version_id: _Optional[str] = ...) -> None: ...

class SetActivePolicyVersionResponse(_message.Message):
    __slots__ = ("policy_id", "policy_key", "active_version_id", "policy_label_conflicts")
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_LABEL_CONFLICTS_FIELD_NUMBER: _ClassVar[int]
    policy_id: str
    policy_key: str
    active_version_id: str
    policy_label_conflicts: _containers.RepeatedCompositeFieldContainer[_errs_pb2.PolicyLabelConflict]
    def __init__(self, policy_id: _Optional[str] = ..., policy_key: _Optional[str] = ..., active_version_id: _Optional[str] = ..., policy_label_conflicts: _Optional[_Iterable[_Union[_errs_pb2.PolicyLabelConflict, _Mapping]]] = ...) -> None: ...

class ExpungePolicyVersionRequest(_message.Message):
    __slots__ = ("version_id",)
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    version_id: str
    def __init__(self, version_id: _Optional[str] = ...) -> None: ...

class ExpungePolicyVersionResponse(_message.Message):
    __slots__ = ("version_id", "expunged")
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    EXPUNGED_FIELD_NUMBER: _ClassVar[int]
    version_id: str
    expunged: bool
    def __init__(self, version_id: _Optional[str] = ..., expunged: bool = ...) -> None: ...

class UnexpungePolicyVersionRequest(_message.Message):
    __slots__ = ("version_id",)
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    version_id: str
    def __init__(self, version_id: _Optional[str] = ...) -> None: ...

class UnexpungePolicyVersionResponse(_message.Message):
    __slots__ = ("version_id", "expunged")
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    EXPUNGED_FIELD_NUMBER: _ClassVar[int]
    version_id: str
    expunged: bool
    def __init__(self, version_id: _Optional[str] = ..., expunged: bool = ...) -> None: ...

class ValidatePolicyRequest(_message.Message):
    __slots__ = ("policy_draft",)
    POLICY_DRAFT_FIELD_NUMBER: _ClassVar[int]
    policy_draft: str
    def __init__(self, policy_draft: _Optional[str] = ...) -> None: ...

class ValidatePolicyResponse(_message.Message):
    __slots__ = ("valid", "labels", "error")
    VALID_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    labels: _containers.RepeatedScalarFieldContainer[str]
    error: _shared_pb2.CompilationError
    def __init__(self, valid: bool = ..., labels: _Optional[_Iterable[str]] = ..., error: _Optional[_Union[_shared_pb2.CompilationError, _Mapping]] = ...) -> None: ...

class TestPolicyOptions(_message.Message):
    __slots__ = ("bypass_cache", "expedited")
    BYPASS_CACHE_FIELD_NUMBER: _ClassVar[int]
    EXPEDITED_FIELD_NUMBER: _ClassVar[int]
    bypass_cache: bool
    expedited: bool
    def __init__(self, bypass_cache: bool = ..., expedited: bool = ...) -> None: ...

class TestPolicyWithDatasetItemsRequest(_message.Message):
    __slots__ = ("policy_draft", "dataset_item_ids", "threshold", "options")
    POLICY_DRAFT_FIELD_NUMBER: _ClassVar[int]
    DATASET_ITEM_IDS_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    policy_draft: str
    dataset_item_ids: _containers.RepeatedScalarFieldContainer[str]
    threshold: float
    options: TestPolicyOptions
    def __init__(self, policy_draft: _Optional[str] = ..., dataset_item_ids: _Optional[_Iterable[str]] = ..., threshold: _Optional[float] = ..., options: _Optional[_Union[TestPolicyOptions, _Mapping]] = ...) -> None: ...

class TestPolicyRequest(_message.Message):
    __slots__ = ("policy_draft", "content_data", "threshold", "options")
    POLICY_DRAFT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    policy_draft: str
    content_data: _containers.RepeatedCompositeFieldContainer[_public_pb2.ContentData]
    threshold: float
    options: TestPolicyOptions
    def __init__(self, policy_draft: _Optional[str] = ..., content_data: _Optional[_Iterable[_Union[_public_pb2.ContentData, _Mapping]]] = ..., threshold: _Optional[float] = ..., options: _Optional[_Union[TestPolicyOptions, _Mapping]] = ...) -> None: ...

class TestPolicyResponse(_message.Message):
    __slots__ = ("job_id", "policy_valid", "error", "report", "content_hash", "policy_draft_id")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_VALID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    REPORT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    POLICY_DRAFT_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    policy_valid: bool
    error: _shared_pb2.CompilationError
    report: _public_pb2.PolicyEvaluationReport
    content_hash: str
    policy_draft_id: str
    def __init__(self, job_id: _Optional[str] = ..., policy_valid: bool = ..., error: _Optional[_Union[_shared_pb2.CompilationError, _Mapping]] = ..., report: _Optional[_Union[_public_pb2.PolicyEvaluationReport, _Mapping]] = ..., content_hash: _Optional[str] = ..., policy_draft_id: _Optional[str] = ...) -> None: ...

class CompiledPolicyMetadata(_message.Message):
    __slots__ = ("committer", "message")
    COMMITTER_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    committer: str
    message: str
    def __init__(self, committer: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class CreatePolicyRequest(_message.Message):
    __slots__ = ("policy_key", "version_text", "dataset_id", "metadata")
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    VERSION_TEXT_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    policy_key: str
    version_text: str
    dataset_id: str
    metadata: CompiledPolicyMetadata
    def __init__(self, policy_key: _Optional[str] = ..., version_text: _Optional[str] = ..., dataset_id: _Optional[str] = ..., metadata: _Optional[_Union[CompiledPolicyMetadata, _Mapping]] = ...) -> None: ...

class CreatePolicyResponse(_message.Message):
    __slots__ = ("valid", "error", "policy_id", "policy_key", "version_id", "dataset_id")
    VALID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    error: _shared_pb2.CompilationError
    policy_id: str
    policy_key: str
    version_id: str
    dataset_id: str
    def __init__(self, valid: bool = ..., error: _Optional[_Union[_shared_pb2.CompilationError, _Mapping]] = ..., policy_id: _Optional[str] = ..., policy_key: _Optional[str] = ..., version_id: _Optional[str] = ..., dataset_id: _Optional[str] = ...) -> None: ...

class CreatePolicyVersionRequest(_message.Message):
    __slots__ = ("policy_id", "version_text", "metadata", "activate")
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_TEXT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ACTIVATE_FIELD_NUMBER: _ClassVar[int]
    policy_id: str
    version_text: str
    metadata: CompiledPolicyMetadata
    activate: bool
    def __init__(self, policy_id: _Optional[str] = ..., version_text: _Optional[str] = ..., metadata: _Optional[_Union[CompiledPolicyMetadata, _Mapping]] = ..., activate: bool = ...) -> None: ...

class CreatePolicyVersionResponse(_message.Message):
    __slots__ = ("valid", "error", "policy_id", "policy_key", "version_id")
    VALID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    error: _shared_pb2.CompilationError
    policy_id: str
    policy_key: str
    version_id: str
    def __init__(self, valid: bool = ..., error: _Optional[_Union[_shared_pb2.CompilationError, _Mapping]] = ..., policy_id: _Optional[str] = ..., policy_key: _Optional[str] = ..., version_id: _Optional[str] = ...) -> None: ...

class GeneratePolicyTask(_message.Message):
    __slots__ = ("id", "customer_id", "policy_id", "policy_version_id", "dataset_id", "policy_name", "policy_text", "created_at", "updated_at", "created_by", "status", "archived_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_NAME_FIELD_NUMBER: _ClassVar[int]
    POLICY_TEXT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ARCHIVED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    customer_id: str
    policy_id: str
    policy_version_id: str
    dataset_id: str
    policy_name: str
    policy_text: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    created_by: str
    status: GeneratePolicyTaskStatus
    archived_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., customer_id: _Optional[str] = ..., policy_id: _Optional[str] = ..., policy_version_id: _Optional[str] = ..., dataset_id: _Optional[str] = ..., policy_name: _Optional[str] = ..., policy_text: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_by: _Optional[str] = ..., status: _Optional[_Union[GeneratePolicyTaskStatus, str]] = ..., archived_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GeneratePolicyFromDatasetRequest(_message.Message):
    __slots__ = ("dataset_id", "policy_name")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_NAME_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    policy_name: str
    def __init__(self, dataset_id: _Optional[str] = ..., policy_name: _Optional[str] = ...) -> None: ...

class GeneratePolicyFromDatasetResponse(_message.Message):
    __slots__ = ("task",)
    TASK_FIELD_NUMBER: _ClassVar[int]
    task: GeneratePolicyTask
    def __init__(self, task: _Optional[_Union[GeneratePolicyTask, _Mapping]] = ...) -> None: ...

class ListGeneratePolicyTasksRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListGeneratePolicyTasksResponse(_message.Message):
    __slots__ = ("tasks",)
    TASKS_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[GeneratePolicyTask]
    def __init__(self, tasks: _Optional[_Iterable[_Union[GeneratePolicyTask, _Mapping]]] = ...) -> None: ...

class ArchiveGeneratePolicyTaskRequest(_message.Message):
    __slots__ = ("policy_task_id",)
    POLICY_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    policy_task_id: str
    def __init__(self, policy_task_id: _Optional[str] = ...) -> None: ...

class ArchiveGeneratePolicyTaskResponse(_message.Message):
    __slots__ = ("task",)
    TASK_FIELD_NUMBER: _ClassVar[int]
    task: GeneratePolicyTask
    def __init__(self, task: _Optional[_Union[GeneratePolicyTask, _Mapping]] = ...) -> None: ...
