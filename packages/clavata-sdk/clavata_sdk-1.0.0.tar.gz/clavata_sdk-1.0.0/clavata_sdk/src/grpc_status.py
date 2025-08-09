from enum import IntEnum, auto, unique

import grpc
from typing_extensions import Self


@unique
class GrpcStatusCode(IntEnum):
    """
    Mirrors grpc_status_code in the gRPC Core.
    """

    OK = 0
    CANCELLED = auto()
    UNKNOWN = auto()
    INVALID_ARGUMENT = auto()
    DEADLINE_EXCEEDED = auto()
    NOT_FOUND = auto()
    ALREADY_EXISTS = auto()
    PERMISSION_DENIED = auto()
    RESOURCE_EXHAUSTED = auto()
    FAILED_PRECONDITION = auto()
    ABORTED = auto()
    UNIMPLEMENTED = auto()
    INTERNAL = auto()
    UNAVAILABLE = auto()
    DATA_LOSS = auto()
    UNAUTHENTICATED = auto()

    @classmethod
    def from_statuscode(cls, status_code: grpc.StatusCode) -> Self:
        # In the official enum, the first value in the tuple is the integer value we want.
        c = status_code.value[0]
        return cls(c)
