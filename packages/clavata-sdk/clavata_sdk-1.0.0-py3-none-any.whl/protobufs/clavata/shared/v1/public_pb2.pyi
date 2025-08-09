from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.api import field_info_pb2 as _field_info_pb2
from google.api import visibility_pb2 as _visibility_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Outcome(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OUTCOME_UNSPECIFIED: _ClassVar[Outcome]
    OUTCOME_FALSE: _ClassVar[Outcome]
    OUTCOME_TRUE: _ClassVar[Outcome]
    OUTCOME_FAILED: _ClassVar[Outcome]

class JobStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_STATUS_UNSPECIFIED: _ClassVar[JobStatus]
    JOB_STATUS_PENDING: _ClassVar[JobStatus]
    JOB_STATUS_RUNNING: _ClassVar[JobStatus]
    JOB_STATUS_COMPLETED: _ClassVar[JobStatus]
    JOB_STATUS_FAILED: _ClassVar[JobStatus]
    JOB_STATUS_CANCELED: _ClassVar[JobStatus]
OUTCOME_UNSPECIFIED: Outcome
OUTCOME_FALSE: Outcome
OUTCOME_TRUE: Outcome
OUTCOME_FAILED: Outcome
JOB_STATUS_UNSPECIFIED: JobStatus
JOB_STATUS_PENDING: JobStatus
JOB_STATUS_RUNNING: JobStatus
JOB_STATUS_COMPLETED: JobStatus
JOB_STATUS_FAILED: JobStatus
JOB_STATUS_CANCELED: JobStatus

class ContentData(_message.Message):
    __slots__ = ("content_hash", "text", "image", "image_url", "video_url", "audio_url", "labels", "content_type", "metadata", "title")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    VIDEO_URL_FIELD_NUMBER: _ClassVar[int]
    AUDIO_URL_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    content_hash: str
    text: str
    image: bytes
    image_url: str
    video_url: str
    audio_url: str
    labels: _containers.RepeatedScalarFieldContainer[str]
    content_type: str
    metadata: _containers.ScalarMap[str, str]
    title: str
    def __init__(self, content_hash: _Optional[str] = ..., text: _Optional[str] = ..., image: _Optional[bytes] = ..., image_url: _Optional[str] = ..., video_url: _Optional[str] = ..., audio_url: _Optional[str] = ..., labels: _Optional[_Iterable[str]] = ..., content_type: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ..., title: _Optional[str] = ...) -> None: ...

class SourceRange(_message.Message):
    __slots__ = ("start", "end")
    class SourceLocation(_message.Message):
        __slots__ = ("line", "column")
        LINE_FIELD_NUMBER: _ClassVar[int]
        COLUMN_FIELD_NUMBER: _ClassVar[int]
        line: int
        column: int
        def __init__(self, line: _Optional[int] = ..., column: _Optional[int] = ...) -> None: ...
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    start: SourceRange.SourceLocation
    end: SourceRange.SourceLocation
    def __init__(self, start: _Optional[_Union[SourceRange.SourceLocation, _Mapping]] = ..., end: _Optional[_Union[SourceRange.SourceLocation, _Mapping]] = ...) -> None: ...

class PolicyEvaluationReport(_message.Message):
    __slots__ = ("policy_id", "policy_key", "policy_version_id", "name", "result", "section_evaluation_reports", "exception_evaluation_report", "content_hash", "content_metadata", "review_result", "threshold", "feature_reports")
    class ReviewResult(_message.Message):
        __slots__ = ("outcome", "score")
        OUTCOME_FIELD_NUMBER: _ClassVar[int]
        SCORE_FIELD_NUMBER: _ClassVar[int]
        outcome: Outcome
        score: float
        def __init__(self, outcome: _Optional[_Union[Outcome, str]] = ..., score: _Optional[float] = ...) -> None: ...
    class AssertionEvaluationReport(_message.Message):
        __slots__ = ("result", "message", "source_range", "score")
        RESULT_FIELD_NUMBER: _ClassVar[int]
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        SOURCE_RANGE_FIELD_NUMBER: _ClassVar[int]
        SCORE_FIELD_NUMBER: _ClassVar[int]
        result: Outcome
        message: str
        source_range: SourceRange
        score: float
        def __init__(self, result: _Optional[_Union[Outcome, str]] = ..., message: _Optional[str] = ..., source_range: _Optional[_Union[SourceRange, _Mapping]] = ..., score: _Optional[float] = ...) -> None: ...
    class ExceptionEvaluationReport(_message.Message):
        __slots__ = ("result", "assertion_evaluation_reports", "source_range", "review_result")
        RESULT_FIELD_NUMBER: _ClassVar[int]
        ASSERTION_EVALUATION_REPORTS_FIELD_NUMBER: _ClassVar[int]
        SOURCE_RANGE_FIELD_NUMBER: _ClassVar[int]
        REVIEW_RESULT_FIELD_NUMBER: _ClassVar[int]
        result: Outcome
        assertion_evaluation_reports: _containers.RepeatedCompositeFieldContainer[PolicyEvaluationReport.AssertionEvaluationReport]
        source_range: SourceRange
        review_result: PolicyEvaluationReport.ReviewResult
        def __init__(self, result: _Optional[_Union[Outcome, str]] = ..., assertion_evaluation_reports: _Optional[_Iterable[_Union[PolicyEvaluationReport.AssertionEvaluationReport, _Mapping]]] = ..., source_range: _Optional[_Union[SourceRange, _Mapping]] = ..., review_result: _Optional[_Union[PolicyEvaluationReport.ReviewResult, _Mapping]] = ...) -> None: ...
    class SectionEvaluationReport(_message.Message):
        __slots__ = ("name", "result", "message", "assertion_evaluation_reports", "exception_evaluation_report", "source_range", "review_result")
        NAME_FIELD_NUMBER: _ClassVar[int]
        RESULT_FIELD_NUMBER: _ClassVar[int]
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        ASSERTION_EVALUATION_REPORTS_FIELD_NUMBER: _ClassVar[int]
        EXCEPTION_EVALUATION_REPORT_FIELD_NUMBER: _ClassVar[int]
        SOURCE_RANGE_FIELD_NUMBER: _ClassVar[int]
        REVIEW_RESULT_FIELD_NUMBER: _ClassVar[int]
        name: str
        result: Outcome
        message: str
        assertion_evaluation_reports: _containers.RepeatedCompositeFieldContainer[PolicyEvaluationReport.AssertionEvaluationReport]
        exception_evaluation_report: PolicyEvaluationReport.ExceptionEvaluationReport
        source_range: SourceRange
        review_result: PolicyEvaluationReport.ReviewResult
        def __init__(self, name: _Optional[str] = ..., result: _Optional[_Union[Outcome, str]] = ..., message: _Optional[str] = ..., assertion_evaluation_reports: _Optional[_Iterable[_Union[PolicyEvaluationReport.AssertionEvaluationReport, _Mapping]]] = ..., exception_evaluation_report: _Optional[_Union[PolicyEvaluationReport.ExceptionEvaluationReport, _Mapping]] = ..., source_range: _Optional[_Union[SourceRange, _Mapping]] = ..., review_result: _Optional[_Union[PolicyEvaluationReport.ReviewResult, _Mapping]] = ...) -> None: ...
    class ContentMetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class FeatureReport(_message.Message):
        __slots__ = ("feature_id", "expression", "score", "source_ranges")
        FEATURE_ID_FIELD_NUMBER: _ClassVar[int]
        EXPRESSION_FIELD_NUMBER: _ClassVar[int]
        SCORE_FIELD_NUMBER: _ClassVar[int]
        SOURCE_RANGES_FIELD_NUMBER: _ClassVar[int]
        feature_id: int
        expression: str
        score: float
        source_ranges: _containers.RepeatedCompositeFieldContainer[SourceRange]
        def __init__(self, feature_id: _Optional[int] = ..., expression: _Optional[str] = ..., score: _Optional[float] = ..., source_ranges: _Optional[_Iterable[_Union[SourceRange, _Mapping]]] = ...) -> None: ...
    class FeatureReportsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: PolicyEvaluationReport.FeatureReport
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PolicyEvaluationReport.FeatureReport, _Mapping]] = ...) -> None: ...
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    SECTION_EVALUATION_REPORTS_FIELD_NUMBER: _ClassVar[int]
    EXCEPTION_EVALUATION_REPORT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    CONTENT_METADATA_FIELD_NUMBER: _ClassVar[int]
    REVIEW_RESULT_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    FEATURE_REPORTS_FIELD_NUMBER: _ClassVar[int]
    policy_id: str
    policy_key: str
    policy_version_id: str
    name: str
    result: Outcome
    section_evaluation_reports: _containers.RepeatedCompositeFieldContainer[PolicyEvaluationReport.SectionEvaluationReport]
    exception_evaluation_report: PolicyEvaluationReport.ExceptionEvaluationReport
    content_hash: str
    content_metadata: _containers.ScalarMap[str, str]
    review_result: PolicyEvaluationReport.ReviewResult
    threshold: float
    feature_reports: _containers.MessageMap[str, PolicyEvaluationReport.FeatureReport]
    def __init__(self, policy_id: _Optional[str] = ..., policy_key: _Optional[str] = ..., policy_version_id: _Optional[str] = ..., name: _Optional[str] = ..., result: _Optional[_Union[Outcome, str]] = ..., section_evaluation_reports: _Optional[_Iterable[_Union[PolicyEvaluationReport.SectionEvaluationReport, _Mapping]]] = ..., exception_evaluation_report: _Optional[_Union[PolicyEvaluationReport.ExceptionEvaluationReport, _Mapping]] = ..., content_hash: _Optional[str] = ..., content_metadata: _Optional[_Mapping[str, str]] = ..., review_result: _Optional[_Union[PolicyEvaluationReport.ReviewResult, _Mapping]] = ..., threshold: _Optional[float] = ..., feature_reports: _Optional[_Mapping[str, PolicyEvaluationReport.FeatureReport]] = ...) -> None: ...

class TimeRange(_message.Message):
    __slots__ = ("start", "end", "inclusive")
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    INCLUSIVE_FIELD_NUMBER: _ClassVar[int]
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    inclusive: bool
    def __init__(self, start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., inclusive: bool = ...) -> None: ...

class JobResult(_message.Message):
    __slots__ = ("uuid", "job_uuid", "content_hash", "report", "created")
    UUID_FIELD_NUMBER: _ClassVar[int]
    JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    REPORT_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    job_uuid: str
    content_hash: str
    report: PolicyEvaluationReport
    created: _timestamp_pb2.Timestamp
    def __init__(self, uuid: _Optional[str] = ..., job_uuid: _Optional[str] = ..., content_hash: _Optional[str] = ..., report: _Optional[_Union[PolicyEvaluationReport, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Job(_message.Message):
    __slots__ = ("job_uuid", "customer_id", "status", "metadata", "content_data", "results", "created", "updated", "completed", "policy_id", "policy_version_id", "policy_draft_id", "threshold")
    class Metadata(_message.Message):
        __slots__ = ("customer_id", "threshold")
        CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
        THRESHOLD_FIELD_NUMBER: _ClassVar[int]
        customer_id: str
        threshold: float
        def __init__(self, customer_id: _Optional[str] = ..., threshold: _Optional[float] = ...) -> None: ...
    JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_DRAFT_ID_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    job_uuid: str
    customer_id: str
    status: JobStatus
    metadata: Job.Metadata
    content_data: _containers.RepeatedCompositeFieldContainer[ContentData]
    results: _containers.RepeatedCompositeFieldContainer[JobResult]
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    completed: _timestamp_pb2.Timestamp
    policy_id: str
    policy_version_id: str
    policy_draft_id: str
    threshold: float
    def __init__(self, job_uuid: _Optional[str] = ..., customer_id: _Optional[str] = ..., status: _Optional[_Union[JobStatus, str]] = ..., metadata: _Optional[_Union[Job.Metadata, _Mapping]] = ..., content_data: _Optional[_Iterable[_Union[ContentData, _Mapping]]] = ..., results: _Optional[_Iterable[_Union[JobResult, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., completed: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., policy_id: _Optional[str] = ..., policy_version_id: _Optional[str] = ..., policy_draft_id: _Optional[str] = ..., threshold: _Optional[float] = ...) -> None: ...
