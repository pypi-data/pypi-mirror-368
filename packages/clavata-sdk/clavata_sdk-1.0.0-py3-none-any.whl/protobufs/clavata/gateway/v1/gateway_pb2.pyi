from clavata.gateway.v1 import errs_pb2 as _errs_pb2
from clavata.shared.v1 import public_pb2 as _public_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.api import visibility_pb2 as _visibility_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GRPCErrorResponse(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class PrecheckFailureResponse(_message.Message):
    __slots__ = ("code", "message", "details")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    details: _containers.RepeatedCompositeFieldContainer[_errs_pb2.PrecheckFailure]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., details: _Optional[_Iterable[_Union[_errs_pb2.PrecheckFailure, _Mapping]]] = ...) -> None: ...

class EvaluateRequest(_message.Message):
    __slots__ = ("content_data", "policy_id", "include_evaluation_report", "threshold", "expedited")
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_EVALUATION_REPORT_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    EXPEDITED_FIELD_NUMBER: _ClassVar[int]
    content_data: _containers.RepeatedCompositeFieldContainer[_public_pb2.ContentData]
    policy_id: str
    include_evaluation_report: bool
    threshold: float
    expedited: bool
    def __init__(self, content_data: _Optional[_Iterable[_Union[_public_pb2.ContentData, _Mapping]]] = ..., policy_id: _Optional[str] = ..., include_evaluation_report: bool = ..., threshold: _Optional[float] = ..., expedited: bool = ...) -> None: ...

class EvaluateResponse(_message.Message):
    __slots__ = ("job_uuid", "content_hash", "policy_evaluation_report")
    JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    POLICY_EVALUATION_REPORT_FIELD_NUMBER: _ClassVar[int]
    job_uuid: str
    content_hash: str
    policy_evaluation_report: _public_pb2.PolicyEvaluationReport
    def __init__(self, job_uuid: _Optional[str] = ..., content_hash: _Optional[str] = ..., policy_evaluation_report: _Optional[_Union[_public_pb2.PolicyEvaluationReport, _Mapping]] = ...) -> None: ...

class CreateJobRequest(_message.Message):
    __slots__ = ("content_data", "policy_id", "wait_for_completion", "threshold", "expedited", "webhook")
    class Webhook(_message.Message):
        __slots__ = ("url", "extra_headers")
        class ExtraHeadersEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: str
            def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        URL_FIELD_NUMBER: _ClassVar[int]
        EXTRA_HEADERS_FIELD_NUMBER: _ClassVar[int]
        url: str
        extra_headers: _containers.ScalarMap[str, str]
        def __init__(self, url: _Optional[str] = ..., extra_headers: _Optional[_Mapping[str, str]] = ...) -> None: ...
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    WAIT_FOR_COMPLETION_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    EXPEDITED_FIELD_NUMBER: _ClassVar[int]
    WEBHOOK_FIELD_NUMBER: _ClassVar[int]
    content_data: _containers.RepeatedCompositeFieldContainer[_public_pb2.ContentData]
    policy_id: str
    wait_for_completion: bool
    threshold: float
    expedited: bool
    webhook: CreateJobRequest.Webhook
    def __init__(self, content_data: _Optional[_Iterable[_Union[_public_pb2.ContentData, _Mapping]]] = ..., policy_id: _Optional[str] = ..., wait_for_completion: bool = ..., threshold: _Optional[float] = ..., expedited: bool = ..., webhook: _Optional[_Union[CreateJobRequest.Webhook, _Mapping]] = ...) -> None: ...

class CreateJobResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: _public_pb2.Job
    def __init__(self, job: _Optional[_Union[_public_pb2.Job, _Mapping]] = ...) -> None: ...

class GetJobRequest(_message.Message):
    __slots__ = ("job_uuid",)
    JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    job_uuid: str
    def __init__(self, job_uuid: _Optional[str] = ...) -> None: ...

class GetJobResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: _public_pb2.Job
    def __init__(self, job: _Optional[_Union[_public_pb2.Job, _Mapping]] = ...) -> None: ...

class ListJobsRequest(_message.Message):
    __slots__ = ("query", "page_size", "page_token")
    class Query(_message.Message):
        __slots__ = ("created_time_range", "updated_time_range", "completed_time_range", "status", "policy_id")
        CREATED_TIME_RANGE_FIELD_NUMBER: _ClassVar[int]
        UPDATED_TIME_RANGE_FIELD_NUMBER: _ClassVar[int]
        COMPLETED_TIME_RANGE_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        POLICY_ID_FIELD_NUMBER: _ClassVar[int]
        created_time_range: _public_pb2.TimeRange
        updated_time_range: _public_pb2.TimeRange
        completed_time_range: _public_pb2.TimeRange
        status: _public_pb2.JobStatus
        policy_id: str
        def __init__(self, created_time_range: _Optional[_Union[_public_pb2.TimeRange, _Mapping]] = ..., updated_time_range: _Optional[_Union[_public_pb2.TimeRange, _Mapping]] = ..., completed_time_range: _Optional[_Union[_public_pb2.TimeRange, _Mapping]] = ..., status: _Optional[_Union[_public_pb2.JobStatus, str]] = ..., policy_id: _Optional[str] = ...) -> None: ...
    QUERY_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    query: ListJobsRequest.Query
    page_size: int
    page_token: str
    def __init__(self, query: _Optional[_Union[ListJobsRequest.Query, _Mapping]] = ..., page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListJobsResponse(_message.Message):
    __slots__ = ("jobs", "next_page_token")
    JOBS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[_public_pb2.Job]
    next_page_token: str
    def __init__(self, jobs: _Optional[_Iterable[_Union[_public_pb2.Job, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...
