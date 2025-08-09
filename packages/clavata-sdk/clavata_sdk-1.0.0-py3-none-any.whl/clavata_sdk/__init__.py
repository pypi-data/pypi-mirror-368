import sys
from pathlib import Path

# Add the protobufs package to the path so that the generated protobuf packages can import each other
CURDIR = Path(__file__).parent
PROTOS_PATH = (CURDIR.parent / "protobufs").resolve()
if str(PROTOS_PATH) not in sys.path:
    # Add our vendored protos as the last entry in the resolution order so that they can be found, but won't
    # take precedence over the user's desired PYTHONPATH or sys.path changes.
    sys.path.append(str(PROTOS_PATH))

from clavata_sdk.src import (
    ClavataClient,
    GetJobRequest,
    ListJobsQuery,
    CreateJobRequest,
    EvaluateRequest,
    GetJobResponse,
    ListJobsQueryBuilder,
    ListJobsResponse,
    CreateJobResponse,
    EvaluateResponse,
    ContentData,
    EvaluateOneRequest,
    EvaluateOneResponse,
    OutcomeName,
    JobStatusName,
    ClavataError,
    EvaluationRefusedError,
    RefusalReason,
)

__all__ = [
    "ClavataClient",
    "GetJobRequest",
    "GetJobResponse",
    "ListJobsQuery",
    "ListJobsQueryBuilder",
    "ListJobsResponse",
    "CreateJobRequest",
    "CreateJobResponse",
    "EvaluateRequest",
    "EvaluateResponse",
    "ContentData",
    "EvaluateOneRequest",
    "EvaluateOneResponse",
    "OutcomeName",
    "JobStatusName",
    "ClavataError",
    "EvaluationRefusedError",
    "RefusalReason",
]
