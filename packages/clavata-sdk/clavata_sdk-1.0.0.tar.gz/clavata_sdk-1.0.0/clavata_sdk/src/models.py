from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, TypeAlias, cast

from google.protobuf import struct_pb2, timestamp_pb2
from google.protobuf.message import Message
from typing_extensions import Self, deprecated

try:
    from protobufs.clavata.gateway.v1 import gateway_pb2
    from protobufs.clavata.shared.v1 import public_pb2
except ImportError:  # Fallback for local dev where protos are vendored under src/protobufs
    from sdk.src.protobufs.clavata.gateway.v1 import gateway_pb2
    from sdk.src.protobufs.clavata.shared.v1 import public_pb2

JsonAny = dict[str, "JsonAny"] | list["JsonAny"] | str | int | float | bool | None
OutcomeName = Literal["TRUE", "FALSE", "FAILED", "UNSPECIFIED"]
JobStatusName = Literal["PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELED"]

LabelName: TypeAlias = str


def to_proto_timestamp(dt: datetime) -> timestamp_pb2.Timestamp:
    return timestamp_pb2.Timestamp(
        seconds=int(dt.timestamp()),
        nanos=int((dt.timestamp() - int(dt.timestamp())) * 1e9),
    )


def from_proto_job_status(
    status: public_pb2.JobStatus,
) -> JobStatusName:
    match status:
        case public_pb2.JOB_STATUS_PENDING:
            return "PENDING"
        case public_pb2.JOB_STATUS_RUNNING:
            return "RUNNING"
        case public_pb2.JOB_STATUS_COMPLETED:
            return "COMPLETED"
        case public_pb2.JOB_STATUS_FAILED:
            return "FAILED"
        case public_pb2.JOB_STATUS_CANCELED:
            return "CANCELED"
        case _:
            raise ValueError(f"Unknown or unspecified job status: {status}")


def to_proto_job_status(status: JobStatusName) -> public_pb2.JobStatus:
    match status:
        case "PENDING":
            return public_pb2.JOB_STATUS_PENDING
        case "RUNNING":
            return public_pb2.JOB_STATUS_RUNNING
        case "COMPLETED":
            return public_pb2.JOB_STATUS_COMPLETED
        case "FAILED":
            return public_pb2.JOB_STATUS_FAILED
        case "CANCELED":
            return public_pb2.JOB_STATUS_CANCELED
        case _:
            raise ValueError(f"Unknown or unspecified job status: {status}")


def from_proto_outcome(outcome: public_pb2.Outcome) -> OutcomeName:
    match outcome:
        case public_pb2.OUTCOME_TRUE:
            return "TRUE"
        case public_pb2.OUTCOME_FALSE:
            return "FALSE"
        case public_pb2.OUTCOME_FAILED:
            return "FAILED"
        case public_pb2.OUTCOME_UNSPECIFIED:
            return "UNSPECIFIED"
        case _:
            raise ValueError(f"Unknown or unspecified outcome: {outcome}")


def to_proto_outcome(outcome: OutcomeName) -> public_pb2.Outcome:
    match outcome:
        case "TRUE":
            return public_pb2.OUTCOME_TRUE
        case "FALSE":
            return public_pb2.OUTCOME_FALSE
        case "FAILED":
            return public_pb2.OUTCOME_FAILED
        case "UNSPECIFIED":
            return public_pb2.OUTCOME_UNSPECIFIED
        case _:
            raise ValueError(f"Unknown or unspecified outcome: {outcome}")


def to_structpb_value(value: JsonAny) -> struct_pb2.Value:
    if isinstance(value, dict):
        return struct_pb2.Value(
            struct_value=struct_pb2.Struct(
                fields={k: to_structpb_value(v) for k, v in value.items()}
            )
        )
    if isinstance(value, list):
        return struct_pb2.Value(
            list_value=struct_pb2.ListValue(values=[to_structpb_value(v) for v in value])
        )
    if isinstance(value, str):
        return struct_pb2.Value(string_value=str(value))
    if isinstance(value, bool):
        return struct_pb2.Value(bool_value=value)
    if isinstance(value, (int, float)):
        return struct_pb2.Value(number_value=value)

    return struct_pb2.Value(null_value=struct_pb2.NULL_VALUE)


def to_report_matches(report: "Report") -> Mapping[LabelName, float]:
    return {
        label.name: label.review_result.score
        for label in report.section_evaluation_reports
        if label.review_result.outcome == "TRUE"
    }


class BaseModel(ABC):
    @abstractmethod
    def to_proto(self) -> Message:
        pass

    @classmethod
    @abstractmethod
    def from_proto(cls, proto: Message) -> Self:
        pass


@dataclass
class ContentData(BaseModel):
    """
    Used to send the request data for the create_job and evaluate methods.

    ### Fields:
    - text: The text content to evaluate.
    - image: The image content to evaluate.
    - metadata: A (optional) map of string keys to string values. Any metadata supplied with a piece of content
        will be returned in the report for that piece of content. This allows you to use your own
        content IDs to match responses to the original content, or to supply any other metadata that
        you may want in the final report.

    #### Note:
    At present, either text or image must be provided. Not both. In the future, we will likely
    add support for both types to be included if they are logically related.
    """

    text: str | None = None
    image: bytes | None = None

    metadata: dict[str, str] = field(default_factory=dict)

    def to_proto(self) -> public_pb2.ContentData:
        return public_pb2.ContentData(
            text=self.text,
            image=self.image,
            metadata=self.metadata,
        )

    @staticmethod
    def from_proto(proto: public_pb2.ContentData) -> "ContentData":
        return ContentData(
            text=proto.text,
            image=proto.image,
            metadata=dict(proto.metadata),
        )


@dataclass
class Webhook(BaseModel):
    url: str
    extra_headers: dict[str, str] = field(default_factory=dict)

    def to_proto(self) -> gateway_pb2.CreateJobRequest.Webhook:
        return gateway_pb2.CreateJobRequest.Webhook(url=self.url, extra_headers=self.extra_headers)

    @classmethod
    def from_proto(cls, proto: gateway_pb2.CreateJobRequest.Webhook) -> "Webhook":
        return cls(url=proto.url, extra_headers=dict(proto.extra_headers))


@dataclass
class CreateJobRequest(BaseModel):
    """
    Used to send the request data for the create_job method.

    ### Fields:
    - content: The content to evaluate. Can be either a single ContentData object or a list of ContentData objects.
    If a single ContentData object is provided, it will be automatically converted to a list. Alternatively, you
    may provide a string, in which case it will be assumed the content is text and a single ContentData object
    will be created with the provided string.
    - policy_id: The ID of the policy to use for content evaluation.
    - wait_for_completion: If True, the request will wait for the job to complete before returning.
    If False, the request will return immediately after the job is created and you can then use a
    GetJobRequest to check the status of the job. If a job is complete, the results will be returned
    in the response.
    - threshold: The threshold to use to determine the outcome of the job. If provided, threshold should
    be a floating point value between 0.0 and 1.0. If not provided, a default value will be set by the server.
    """

    content: list[ContentData] | ContentData | str
    policy_id: str
    wait_for_completion: bool
    threshold: float | None = None
    expedited: bool = False
    webhook: Webhook | None = field(default=None, init=False)

    def __post_init__(self):
        # Ensure that we convert a single ContentData object to a list so we can be confident that it is always a list
        if isinstance(self.content, ContentData):
            self.content = [self.content]
        elif isinstance(self.content, str):
            self.content = [ContentData(text=self.content)]

    @classmethod
    def from_proto(cls, proto: gateway_pb2.CreateJobRequest) -> "CreateJobRequest":
        return cls(
            content=[ContentData.from_proto(content) for content in proto.content_data],
            policy_id=proto.policy_id,
            wait_for_completion=proto.wait_for_completion,
            threshold=proto.threshold,
            expedited=proto.expedited,
        )

    def to_proto(self) -> gateway_pb2.CreateJobRequest:
        return gateway_pb2.CreateJobRequest(
            content_data=[content.to_proto() for content in cast(list[ContentData], self.content)],
            policy_id=self.policy_id,
            wait_for_completion=self.wait_for_completion,
            threshold=self.threshold,
            expedited=self.expedited,
            webhook=self.webhook.to_proto() if self.webhook else None,
        )

    def add_webhook(
        self, url: str, extra_headers: dict[str, str] | None = None
    ) -> "CreateJobRequest":
        """
        Adds a webhook to the create job request. When the job is completed, the server will send a POST request to the
        webhook URL with the job result.

        ### Parameters:
        - url: The URL to send the webhook to.
        - extra_headers: Extra headers to send with the webhook (optional).
        """
        self.webhook = Webhook(url, extra_headers=extra_headers or {})
        return self


@dataclass
class ReviewResult(BaseModel):
    outcome: OutcomeName
    score: float

    def to_proto(self) -> public_pb2.PolicyEvaluationReport.ReviewResult:
        return public_pb2.PolicyEvaluationReport.ReviewResult(
            outcome=to_proto_outcome(self.outcome),
            score=self.score,
        )

    @classmethod
    def from_proto(cls, proto: public_pb2.PolicyEvaluationReport.ReviewResult) -> "ReviewResult":
        return ReviewResult(
            outcome=from_proto_outcome(proto.outcome),
            score=proto.score,
        )


class _ResultMixin:
    """
    This Mixin handles the deprecated result field. So if an integration with the SDK has already used this field,
    it will still work, but a warning will be emitted.
    """

    review_result: ReviewResult

    @property
    @deprecated(
        "Use review_result.outcome instead", category=PendingDeprecationWarning, stacklevel=2
    )
    def result(self) -> OutcomeName:
        return self.review_result.outcome

    @result.setter
    @deprecated(
        "Use review_result.outcome instead", category=PendingDeprecationWarning, stacklevel=2
    )
    def result(self, value: OutcomeName):
        self.review_result.outcome = value


@dataclass
class LabelReport(BaseModel, _ResultMixin):
    name: str
    message: str
    review_result: ReviewResult

    def to_proto(self) -> public_pb2.PolicyEvaluationReport.SectionEvaluationReport:
        return public_pb2.PolicyEvaluationReport.SectionEvaluationReport(
            name=self.name,
            message=self.message,
            result=self.review_result.outcome,
            review_result=self.review_result.to_proto(),
        )

    @staticmethod
    def from_proto(
        proto: public_pb2.PolicyEvaluationReport.SectionEvaluationReport,
    ) -> "LabelReport":
        return LabelReport(
            name=proto.name,
            message=proto.message,
            review_result=ReviewResult.from_proto(proto.review_result),
        )


@dataclass
class Report(BaseModel, _ResultMixin):
    policy_id: str
    policy_name: str
    policy_version_id: str
    section_evaluation_reports: list[LabelReport]
    content_hash: str
    content_metadata: dict[str, str]
    review_result: ReviewResult
    threshold: float

    def to_proto(self) -> public_pb2.PolicyEvaluationReport:
        return public_pb2.PolicyEvaluationReport(
            policy_id=self.policy_id,
            policy_key=self.policy_name,
            policy_version_id=self.policy_version_id,
            result=self.review_result.outcome,
            section_evaluation_reports=[
                section.to_proto() for section in self.section_evaluation_reports
            ],
            content_hash=self.content_hash,
            content_metadata=self.content_metadata,
            review_result=self.review_result.to_proto(),
            threshold=self.threshold,
        )

    @classmethod
    def from_proto(cls, proto: public_pb2.PolicyEvaluationReport) -> "Report":
        return Report(
            policy_id=proto.policy_id,
            policy_name=proto.policy_key,
            policy_version_id=proto.policy_version_id,
            section_evaluation_reports=[
                LabelReport.from_proto(section) for section in proto.section_evaluation_reports
            ],
            content_hash=proto.content_hash,
            content_metadata=dict(proto.content_metadata),
            review_result=ReviewResult.from_proto(proto.review_result),
            threshold=proto.threshold,
        )


@dataclass
class JobResult(BaseModel):
    """
    The result of a job.

    ### Fields:
    - uuid: The UUID of the job result.
    - job_uuid: The UUID of the job that was created.
    - content_hash: The hash of the content that was evaluated.
    - report: The full evaluation report for this policy/content pair.
    - created: The date and time the job was created.
    - matches: If you don't need all the information from the report, this field is a mapping of label names to their
    match scores. Only labels that had scores which exceeded the threshold (evaluated to TRUE) are included in the mapping.
    """

    uuid: str
    job_uuid: str
    content_hash: str
    report: Report
    created: datetime

    matches: Mapping[LabelName, float]

    def to_proto(self) -> public_pb2.JobResult:
        return public_pb2.JobResult(
            uuid=self.uuid,
            job_uuid=self.job_uuid,
            content_hash=self.content_hash,
            report=self.report.to_proto(),
            created=to_proto_timestamp(self.created),
        )

    @staticmethod
    def from_proto(proto: public_pb2.JobResult) -> "JobResult":
        report = Report.from_proto(proto.report)
        matches = to_report_matches(report)
        return JobResult(
            uuid=proto.uuid,
            job_uuid=proto.job_uuid,
            content_hash=proto.content_hash,
            report=report,
            created=proto.created.ToDatetime(),
            matches=matches,
        )


@dataclass
class Job(BaseModel):
    job_uuid: str
    customer_id: str
    policy_id: str
    policy_version_id: str
    status: JobStatusName
    content_data: list[ContentData]
    results: list[JobResult]
    created: datetime
    updated: datetime
    completed: datetime
    threshold: float

    def to_proto(self) -> public_pb2.Job:
        return public_pb2.Job(
            job_uuid=self.job_uuid,
            customer_id=self.customer_id,
            policy_id=self.policy_id,
            policy_version_id=self.policy_version_id,
            status=to_proto_job_status(self.status),
            content_data=[content.to_proto() for content in self.content_data],
            results=[result.to_proto() for result in self.results],
            created=to_proto_timestamp(self.created),
            updated=to_proto_timestamp(self.updated),
            completed=to_proto_timestamp(self.completed),
            threshold=self.threshold,
        )

    @classmethod
    def from_proto(cls, proto: public_pb2.Job) -> "Job":
        return Job(
            job_uuid=proto.job_uuid,
            customer_id=proto.customer_id,
            policy_id=proto.policy_id,
            policy_version_id=proto.policy_version_id,
            status=from_proto_job_status(proto.status),
            content_data=[ContentData.from_proto(content) for content in proto.content_data],
            results=[JobResult.from_proto(result) for result in proto.results],
            created=proto.created.ToDatetime(),
            updated=proto.updated.ToDatetime(),
            completed=proto.completed.ToDatetime(),
            threshold=proto.threshold,
        )


@dataclass
class CreateJobResponse(Job):
    def to_proto(self) -> gateway_pb2.CreateJobResponse:
        return gateway_pb2.CreateJobResponse(job=super().to_proto())

    @classmethod
    def from_proto(cls, proto: gateway_pb2.CreateJobResponse) -> "CreateJobResponse":
        job = super().from_proto(proto.job)
        return CreateJobResponse(**job.__dict__)


@dataclass
class EvaluateRequest(BaseModel):
    """
    Used to send the request data for the evaluate method.

    ### Fields:
    - content: The content to evaluate. Can be either a single ContentData object or a list of ContentData objects.
    If a single ContentData object is provided, it will be automatically converted to a list.
    - policy_id: The ID of the policy to evaluate the content against.
    - include_evaluation_report: Whether to include the full evaluation report in the response. If False, only the result for
    the entire policy is returned. Defaults to True.
    - threshold: The threshold to use to determine the outcome of the job. If provided, threshold should
    be a floating point value between 0.0 and 1.0. If not provided, a default value will be set by the server.
    """

    content: list[ContentData] | ContentData | str
    policy_id: str
    include_evaluation_report: bool = True
    threshold: float | None = None
    expedited: bool = False

    def __post_init__(self):
        # Ensure that we convert a single ContentData object to a list so we can be confident that it is always a list
        if isinstance(self.content, ContentData):
            self.content = [self.content]
        elif isinstance(self.content, str):
            self.content = [ContentData(text=self.content)]

    @classmethod
    def from_proto(cls, proto: gateway_pb2.EvaluateRequest) -> "EvaluateRequest":
        return cls(
            content=[ContentData.from_proto(content) for content in proto.content_data],
            policy_id=proto.policy_id,
            include_evaluation_report=proto.include_evaluation_report,
            threshold=proto.threshold,
            expedited=proto.expedited,
        )

    def to_proto(self) -> gateway_pb2.EvaluateRequest:
        return gateway_pb2.EvaluateRequest(
            content_data=[content.to_proto() for content in cast(list[ContentData], self.content)],
            policy_id=self.policy_id,
            include_evaluation_report=self.include_evaluation_report,
            threshold=self.threshold,
            expedited=self.expedited,
        )


@dataclass
class EvaluateResponse(BaseModel):
    """
    The response from the evaluate method.

    ### Fields:
    - job_uuid: The UUID of the job that was created.
    - content_hash: The hash of the content that was evaluated.
    - policy_evaluation_report: The full evaluation report for the policy.
    - matches: If you don't need all the information from the report, this field is a mapping of label names to their
    match scores. Only labels that had scores which exceeded the threshold (evaluated to TRUE) are included in the mapping.
    """

    job_uuid: str
    content_hash: str
    policy_evaluation_report: Report
    matches: Mapping[LabelName, float]

    def to_proto(self) -> gateway_pb2.EvaluateResponse:
        return gateway_pb2.EvaluateResponse(
            job_uuid=self.job_uuid,
            content_hash=self.content_hash,
            policy_evaluation_report=self.policy_evaluation_report.to_proto(),
        )

    @staticmethod
    def from_proto(proto: gateway_pb2.EvaluateResponse) -> "EvaluateResponse":
        report = Report.from_proto(proto.policy_evaluation_report)
        matches = to_report_matches(report)
        return EvaluateResponse(
            job_uuid=proto.job_uuid,
            content_hash=proto.content_hash,
            policy_evaluation_report=report,
            matches=matches,
        )


@dataclass
class EvaluateOneRequest(BaseModel):
    content: ContentData | str
    policy_id: str
    wait_for_completion: bool
    threshold: float | None = None
    expedited: bool = False

    def __post_init__(self):
        if isinstance(self.content, str):
            self.content = ContentData(text=self.content)

    def to_proto(self) -> gateway_pb2.CreateJobRequest:
        return gateway_pb2.CreateJobRequest(
            content_data=[cast(ContentData, self.content).to_proto()],
            policy_id=self.policy_id,
            wait_for_completion=self.wait_for_completion,
            threshold=self.threshold,
            expedited=self.expedited,
        )

    @classmethod
    def from_proto(cls, proto: gateway_pb2.CreateJobRequest) -> "EvaluateOneRequest":
        raise NotImplementedError("EvaluateOneRequest is not implemented")


@dataclass
class EvaluateOneResponse(BaseModel):
    job_uuid: str
    content_hash: str
    report: Report
    status: JobStatusName

    def to_proto(self) -> gateway_pb2.CreateJobResponse:
        raise NotImplementedError("EvaluateOneResponse is not implemented")

    @classmethod
    def from_proto(cls, proto: gateway_pb2.CreateJobResponse) -> "EvaluateOneResponse":
        # Get the one result to work from
        result = proto.job.results[0]
        return cls(
            job_uuid=proto.job.job_uuid,
            content_hash=result.content_hash,
            report=Report.from_proto(result.report),
            status=from_proto_job_status(proto.job.status),
        )


@dataclass
class TimeRange(BaseModel):
    start: datetime
    end: datetime
    inclusive: bool

    def to_proto(self) -> public_pb2.TimeRange:
        return public_pb2.TimeRange(
            start=to_proto_timestamp(self.start),
            end=to_proto_timestamp(self.end),
            inclusive=self.inclusive,
        )

    @classmethod
    def from_proto(cls, proto: public_pb2.TimeRange) -> "TimeRange":
        return TimeRange(
            start=proto.start.ToDatetime(),
            end=proto.end.ToDatetime(),
            inclusive=proto.inclusive,
        )


@dataclass
class ListJobsQuery(BaseModel):
    created_time_range: TimeRange | None = None
    updated_time_range: TimeRange | None = None
    completed_time_range: TimeRange | None = None
    status: JobStatusName | None = None
    page_size: int | None = None
    _next_page_token: str | None = field(default=None, init=False)

    def to_proto(self) -> gateway_pb2.ListJobsRequest.Query:
        created_time_range = self.created_time_range.to_proto() if self.created_time_range else None
        updated_time_range = self.updated_time_range.to_proto() if self.updated_time_range else None
        completed_time_range = (
            self.completed_time_range.to_proto() if self.completed_time_range else None
        )
        status = to_proto_job_status(self.status) if self.status else None

        return gateway_pb2.ListJobsRequest.Query(
            created_time_range=created_time_range,
            updated_time_range=updated_time_range,
            completed_time_range=completed_time_range,
            status=status,
        )

    def to_proto_request(self) -> gateway_pb2.ListJobsRequest:
        return gateway_pb2.ListJobsRequest(
            query=self.to_proto(), page_size=self.page_size, page_token=self._next_page_token
        )

    @classmethod
    def from_proto(cls, proto: gateway_pb2.ListJobsRequest.Query) -> "ListJobsQuery":
        return cls(
            created_time_range=TimeRange.from_proto(proto.created_time_range),
            updated_time_range=TimeRange.from_proto(proto.updated_time_range),
            completed_time_range=TimeRange.from_proto(proto.completed_time_range),
            status=from_proto_job_status(proto.status),
        )


class ListJobsQueryBuilder:
    """
    The builder for the ListJobsQuery type allows you to build a query in a more fluent way.

    ### Example:
    ```python
    query = ListJobsQueryBuilder()\
        .set_created_time_range(start, end)\
        .set_updated_time_range(start, end)\
        .set_completed_time_range(start, end)\
        .set_status("COMPLETED")\
        .build()
    ```

    Once you have set all the fields you want to set, call `build()` to obtain the final query.
    """

    query: ListJobsQuery

    def __init__(self):
        self.query = ListJobsQuery()

    def set_created_time_range(
        self, start: datetime, end: datetime, inclusive: bool = True
    ) -> Self:
        """
        Sets the time range when a job was created.
        """
        self.query.created_time_range = TimeRange(start, end, inclusive)
        return self

    def set_updated_time_range(
        self, start: datetime, end: datetime, inclusive: bool = True
    ) -> Self:
        """
        Sets the time range when a job was updated.
        """
        self.query.updated_time_range = TimeRange(start, end, inclusive)
        return self

    def set_completed_time_range(
        self, start: datetime, end: datetime, inclusive: bool = True
    ) -> Self:
        """
        Sets the time range when a job was completed.
        """
        self.query.completed_time_range = TimeRange(start, end, inclusive)
        return self

    def set_status(self, status: JobStatusName) -> Self:
        """
        Sets the status of the jobs to return.
        """
        self.query.status = status
        return self

    def set_page_size(self, page_size: int) -> Self:
        """
        Sets the maximum number of jobs to return per page.
        """
        self.query.page_size = page_size
        return self

    def build(self) -> ListJobsQuery:
        return self.query

    def build_next(self, resp: "ListJobsResponse") -> Self:
        """
        Builds the same query, but uses the last response to ask the server for the next page of results.
        """
        self.query._next_page_token = resp.next_page_token
        return self


@dataclass
class ListJobsResponse(BaseModel):
    jobs: list[Job]
    next_page_token: str | None = None

    def to_proto(self) -> gateway_pb2.ListJobsResponse:
        return gateway_pb2.ListJobsResponse(jobs=[job.to_proto() for job in self.jobs])

    @classmethod
    def from_proto(cls, proto: gateway_pb2.ListJobsResponse) -> "ListJobsResponse":
        return ListJobsResponse(
            jobs=[Job.from_proto(job) for job in proto.jobs],
            next_page_token=proto.next_page_token,
        )


@dataclass
class GetJobRequest(BaseModel):
    job_uuid: str

    def to_proto(self) -> gateway_pb2.GetJobRequest:
        return gateway_pb2.GetJobRequest(job_uuid=self.job_uuid)

    @classmethod
    def from_proto(cls, proto: gateway_pb2.GetJobRequest) -> "GetJobRequest":
        return cls(job_uuid=proto.job_uuid)


@dataclass
class GetJobResponse(Job):
    def to_proto(self) -> gateway_pb2.GetJobResponse:
        return gateway_pb2.GetJobResponse(job=super().to_proto())

    @classmethod
    def from_proto(cls, proto: gateway_pb2.GetJobResponse) -> "GetJobResponse":
        job = super().from_proto(proto.job)
        return GetJobResponse(**job.__dict__)
