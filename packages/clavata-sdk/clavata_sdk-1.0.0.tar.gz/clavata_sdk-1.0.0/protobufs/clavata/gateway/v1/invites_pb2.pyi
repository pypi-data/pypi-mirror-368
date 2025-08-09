from clavata.shared.v1 import shared_pb2 as _shared_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InviteStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVITE_STATUS_UNSPECIFIED: _ClassVar[InviteStatus]
    INVITE_STATUS_PENDING: _ClassVar[InviteStatus]
    INVITE_STATUS_ACCEPTED: _ClassVar[InviteStatus]
    INVITE_STATUS_EXPIRED: _ClassVar[InviteStatus]
INVITE_STATUS_UNSPECIFIED: InviteStatus
INVITE_STATUS_PENDING: InviteStatus
INVITE_STATUS_ACCEPTED: InviteStatus
INVITE_STATUS_EXPIRED: InviteStatus

class InviteRequest(_message.Message):
    __slots__ = ("email", "role", "customer_id", "first_name", "last_name", "redirect_url", "customer_name")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_URL_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_NAME_FIELD_NUMBER: _ClassVar[int]
    email: str
    role: _shared_pb2.Role
    customer_id: str
    first_name: str
    last_name: str
    redirect_url: str
    customer_name: str
    def __init__(self, email: _Optional[str] = ..., role: _Optional[_Union[_shared_pb2.Role, str]] = ..., customer_id: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., redirect_url: _Optional[str] = ..., customer_name: _Optional[str] = ...) -> None: ...

class InviteResponse(_message.Message):
    __slots__ = ("invite_id", "error", "customer_id")
    INVITE_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    invite_id: int
    error: str
    customer_id: str
    def __init__(self, invite_id: _Optional[int] = ..., error: _Optional[str] = ..., customer_id: _Optional[str] = ...) -> None: ...

class RenewInviteRequest(_message.Message):
    __slots__ = ("invite_id", "redirect_url")
    INVITE_ID_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_URL_FIELD_NUMBER: _ClassVar[int]
    invite_id: int
    redirect_url: str
    def __init__(self, invite_id: _Optional[int] = ..., redirect_url: _Optional[str] = ...) -> None: ...

class RenewInviteResponse(_message.Message):
    __slots__ = ("invite_id", "expiration")
    INVITE_ID_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    invite_id: int
    expiration: _timestamp_pb2.Timestamp
    def __init__(self, invite_id: _Optional[int] = ..., expiration: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListInvitesRequest(_message.Message):
    __slots__ = ("query",)
    class Query(_message.Message):
        __slots__ = ("role", "status")
        ROLE_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        role: _shared_pb2.Role
        status: InviteStatus
        def __init__(self, role: _Optional[_Union[_shared_pb2.Role, str]] = ..., status: _Optional[_Union[InviteStatus, str]] = ...) -> None: ...
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: ListInvitesRequest.Query
    def __init__(self, query: _Optional[_Union[ListInvitesRequest.Query, _Mapping]] = ...) -> None: ...

class InvitedUser(_message.Message):
    __slots__ = ("invite_id", "email", "role", "first_name", "last_name", "status", "expiration")
    INVITE_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    invite_id: int
    email: str
    role: _shared_pb2.Role
    first_name: str
    last_name: str
    status: InviteStatus
    expiration: _timestamp_pb2.Timestamp
    def __init__(self, invite_id: _Optional[int] = ..., email: _Optional[str] = ..., role: _Optional[_Union[_shared_pb2.Role, str]] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., status: _Optional[_Union[InviteStatus, str]] = ..., expiration: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListInvitesResponse(_message.Message):
    __slots__ = ("invited_users",)
    INVITED_USERS_FIELD_NUMBER: _ClassVar[int]
    invited_users: _containers.RepeatedCompositeFieldContainer[InvitedUser]
    def __init__(self, invited_users: _Optional[_Iterable[_Union[InvitedUser, _Mapping]]] = ...) -> None: ...

class DeleteInviteRequest(_message.Message):
    __slots__ = ("invite_id",)
    INVITE_ID_FIELD_NUMBER: _ClassVar[int]
    invite_id: int
    def __init__(self, invite_id: _Optional[int] = ...) -> None: ...

class DeleteInviteResponse(_message.Message):
    __slots__ = ("invite_id", "deleted")
    INVITE_ID_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    invite_id: int
    deleted: bool
    def __init__(self, invite_id: _Optional[int] = ..., deleted: bool = ...) -> None: ...
