from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Protocol, cast, runtime_checkable

import grpc
from google.protobuf import any_pb2
from google.protobuf.message import Message
from grpc.aio import Metadata
from typing_extensions import Self

from .grpc_status import GrpcStatusCode

try:
    from protobufs.clavata.gateway.v1.errs_pb2 import PrecheckFailure
    from protobufs.google.rpc import status_pb2
except ImportError:
    # Fallback for local dev where protos are vendored under src/protobufs
    from sdk.src.protobufs.clavata.gateway.v1.errs_pb2 import PrecheckFailure
    from sdk.src.protobufs.google.rpc import status_pb2


@runtime_checkable
class WithMetadata(Protocol):
    """
    A protocol that defines the methods that an object must implement to be used with
    the metadata_to_rich_status function. This is a bit of a workaround so that the type checker
    will let the metadata_to_rich_status function work with any object that has the necessary methods.
    Practically, this applies to the grpc.Call object, but also to the grpc.aio.AioRpcError object and
    its synchronous counterpart, grpc.RpcError.
    """

    def code(self) -> grpc.StatusCode: ...
    def details(self) -> str | None: ...
    def trailing_metadata(self) -> Metadata: ...


GRPC_DETAILS_METADATA_KEY = "grpc-status-details-bin"


def metadata_to_rich_status(wm: WithMetadata) -> status_pb2.Status | None:
    """Returns a google.rpc.status.Status message corresponding to a given grpc.Call.

    This is an EXPERIMENTAL API.

    Args:
      call: A grpc.Call instance.

    Returns:
      A google.rpc.status.Status message representing the status of the RPC.

    Raises:
      ValueError: If the gRPC call's code or details are inconsistent with the
        status code and message inside of the google.rpc.status.Status.
    """
    trailing_metadata = wm.trailing_metadata()
    if trailing_metadata is None:
        return None

    for key, value in trailing_metadata:
        if key == GRPC_DETAILS_METADATA_KEY:
            status_pb2.Status.FromString
            rich_status = status_pb2.Status.FromString(cast(bytes, value))
            grpc_status_code = GrpcStatusCode.from_statuscode(wm.code())
            if grpc_status_code != rich_status.code:
                # If we don't have a match, something went very wrong and we should fail.
                raise ValueError(
                    "Code in Status proto (%s) doesn't match status code (%s)"
                    % (grpc_status_code, wm.code())
                )
            if wm.details() != rich_status.message:
                # If we don't have a match, something went very wrong and we should fail. The "details"
                # field is the same thing as the officially defined "message" field. So these should always
                # match if the parsing to Status proto was successful.
                raise ValueError(
                    "Message in Status proto (%s) doesn't match status details"
                    " (%s)" % (rich_status.message, wm.details())
                )
            return rich_status
    return None


class ClavataError(Exception):
    """
    Base class for all Clavata errors.
    """

    pass


class RefusalReason(IntEnum):
    """
    The reason why the Clavata API refused to evaluate the content.
    """

    UNKNOWN = 0
    CSAM = auto()
    UNSUPPORTED_FORMAT = auto()
    INVALID_CONTENT = auto()

    MAX_VALUE = INVALID_CONTENT


class DecodedStatus:
    """
    DecodedStatus provides a way to keep the original Status object returned by the RPC,
    while also adding the "details" in their decoded form.
    """

    DEFAULT_DECODABLE_TYPES = (PrecheckFailure,)

    _status: status_pb2.Status
    _decoded_details: list[Message]

    def __init__(self, status: status_pb2.Status, decoded_details: list[Message]):
        self._status = status
        self._decoded_details = decoded_details

    @property
    def code(self) -> GrpcStatusCode:
        return GrpcStatusCode(self._status.code)

    @property
    def details(self) -> Sequence[any_pb2.Any]:
        return self._status.details

    @property
    def message(self) -> str:
        return self._status.message

    @property
    def decoded_details(self) -> list[Message]:
        return self._decoded_details

    @classmethod
    def from_rpc_status(cls, status: status_pb2.Status, *decodable_types: type[Message]) -> Self:
        """
        Given a "grpc.Status" object, decode any additional details and return a
        "DecodedStatus" object.
        """
        try:
            # Join the default decodable types with the provided decodable types
            decodable_types = cls.DEFAULT_DECODABLE_TYPES + decodable_types
            decoded_details = cls._decode_status_details(status.details, *decodable_types)
            return cls(status, decoded_details)
        except Exception:
            # If we fail to decode the detais, we return an empty details list.
            return cls(status, [])

    @staticmethod
    def _decode_status_details(
        details: Sequence[any_pb2.Any], *known_types: type[Message]
    ) -> list[Message]:
        """
        Decodes the status details. When they arrive, the "details" are encoded as a list of Any messages.
        By definition, this means that the details are a type_url (which identifies the type of the data)
        and a value (which is binary encoded). To work with the data, we need to identify the correct type
        of each detail value and then unpack it into is correct, generated, protobuf message type.
        """
        mapping = {t.DESCRIPTOR.full_name: t for t in known_types}

        unpacked = []
        for detail in details:
            type_name = detail.TypeName()
            if type_name not in mapping:
                continue

            # Create a new instance of the known type
            msg = mapping[type_name]()

            # Unpack the detail into the new instance. If Unpack returns false, it means it couldn't
            # unpack the value into the instance we created, so we'll skip over it.
            if not detail.Unpack(msg):
                continue

            unpacked.append(msg)

        return unpacked

    def __repr__(self) -> str:
        return f"DecodedStatus(code={self.code}, message={self.message}, details={self.details}, decoded_details={self.decoded_details})"


@dataclass
class RefusedContent:
    """
    When a refusal occurs, we can store each reason with the piece of content that was refused.
    """

    reason: RefusalReason
    content_hash: str


class EvaluationRefusedError(ClavataError):
    """
    An error that is raised when the Clavata API refuses to evaluate the content.
    The "refusals" attribute contains a list of the refusals that occurred and the
    reasons why they occurred.
    """

    refusals: list[RefusedContent] = []
    original_error: grpc.aio.AioRpcError

    def __init__(
        self,
        refusals: list[RefusedContent],
        original_error: grpc.aio.AioRpcError,
    ):
        self.refusals = refusals
        self.original_error = original_error
        super().__init__("refused")

    @property
    def top_reason(self) -> RefusalReason:
        """
        Returns the "most important" refusal reason in the list of refusals. The refusal reasons
        should always be ordered from most important to least, with lower numbers being more important
        (excluding the "UNKNOWN" reason).
        """
        # Set the top_reason to the highest 64 bit integer value
        top_reason = RefusalReason.MAX_VALUE + 1
        for refusal in self.refusals:
            if refusal.reason == RefusalReason.UNKNOWN:
                continue

            top_reason = min(top_reason, refusal.reason)

        if top_reason == RefusalReason.MAX_VALUE + 1:
            return RefusalReason.UNKNOWN

        return RefusalReason(top_reason)

    @property
    def most_common_reason(self) -> RefusalReason:
        """
        Returns the most common refusal reason in the list of refusals.
        """
        return Counter(refusal.reason for refusal in self.refusals).most_common(1)[0][0]

    @property
    def first_reason(self) -> RefusalReason:
        """
        Returns the first refusal reason in the list of refusals.
        """
        try:
            return self.refusals[0].reason
        except IndexError:
            # Sanity check: This shouldn't be possible
            return RefusalReason.UNKNOWN

    @property
    def refused_content_hashes(self) -> list[str]:
        """
        Returns a list of the content hashes that were refused (without their specific reasons).
        Deduplicates the list before returning.
        """
        return list(set(refusal.content_hash for refusal in self.refusals))

    @classmethod
    def from_rpc_error(cls, error: grpc.aio.AioRpcError) -> Self | grpc.aio.AioRpcError:
        """
        Creates an "EvaluationRefusals" error from a grpc.aio.AioRpcError.
        """
        status = metadata_to_rich_status(error)
        if status is None:
            raise error

        decoded_status = DecodedStatus.from_rpc_status(status)
        return cls.from_rpc_status(decoded_status, error)

    @classmethod
    def from_rpc_status(
        cls, status: DecodedStatus, original_error: grpc.aio.AioRpcError
    ) -> Self | grpc.aio.AioRpcError:
        """
        Looks for any refusal reasons in a rpc.Status object and populates the error as appropriate
        """

        if status.code not in (GrpcStatusCode.CANCELLED, GrpcStatusCode.FAILED_PRECONDITION):
            return original_error

        refusals = []
        for detail in status.decoded_details:
            if not isinstance(detail, PrecheckFailure):
                continue

            refusals.append(
                RefusedContent(
                    # Since we've aligned the type enum in our protobufs with the refusal reason enum,
                    # we can just cast the type to the reason enum.
                    reason=RefusalReason(detail.type),
                    # The server sets the content hash as a string value on the "Details" field.
                    content_hash=detail.details.string_value,
                )
            )

        # If for some reason we couldn't find any PrecheckFailures, we'll add a single refusal
        # with the "UNKNOWN" reason.
        if len(refusals) == 0:
            refusals.append(
                RefusedContent(
                    reason=RefusalReason.UNKNOWN,
                    content_hash="",
                )
            )

        return cls(refusals=refusals, original_error=original_error)
