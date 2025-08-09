from clavata.shared.v1 import shared_pb2 as _shared_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class APITokenStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    API_TOKEN_UNSPECIFIED: _ClassVar[APITokenStatus]
    API_TOKEN_ENABLED: _ClassVar[APITokenStatus]
    API_TOKEN_DISABLED: _ClassVar[APITokenStatus]
    API_TOKEN_REVOKED: _ClassVar[APITokenStatus]
API_TOKEN_UNSPECIFIED: APITokenStatus
API_TOKEN_ENABLED: APITokenStatus
API_TOKEN_DISABLED: APITokenStatus
API_TOKEN_REVOKED: APITokenStatus

class GenerateAPITokenRequest(_message.Message):
    __slots__ = ("duration", "name", "user_id")
    DURATION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    duration: _duration_pb2.Duration
    name: str
    user_id: str
    def __init__(self, duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., name: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class GenerateAPITokenResponse(_message.Message):
    __slots__ = ("user_info", "error", "api_token_id")
    USER_INFO_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    API_TOKEN_ID_FIELD_NUMBER: _ClassVar[int]
    user_info: _shared_pb2.UserInfo
    error: str
    api_token_id: str
    def __init__(self, user_info: _Optional[_Union[_shared_pb2.UserInfo, _Mapping]] = ..., error: _Optional[str] = ..., api_token_id: _Optional[str] = ...) -> None: ...

class ListAllAPITokensRequest(_message.Message):
    __slots__ = ("customer_id",)
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    def __init__(self, customer_id: _Optional[str] = ...) -> None: ...

class APIToken(_message.Message):
    __slots__ = ("id", "created_at", "updated_at", "name", "expires_at", "status", "customer_id", "user_id", "created_by_user_id", "updated_by_user_id", "user_email", "signature")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    name: str
    expires_at: _timestamp_pb2.Timestamp
    status: APITokenStatus
    customer_id: str
    user_id: str
    created_by_user_id: str
    updated_by_user_id: str
    user_email: str
    signature: str
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., name: _Optional[str] = ..., expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[_Union[APITokenStatus, str]] = ..., customer_id: _Optional[str] = ..., user_id: _Optional[str] = ..., created_by_user_id: _Optional[str] = ..., updated_by_user_id: _Optional[str] = ..., user_email: _Optional[str] = ..., signature: _Optional[str] = ...) -> None: ...

class ListAllAPITokensResponse(_message.Message):
    __slots__ = ("api_tokens",)
    API_TOKENS_FIELD_NUMBER: _ClassVar[int]
    api_tokens: _containers.RepeatedCompositeFieldContainer[APIToken]
    def __init__(self, api_tokens: _Optional[_Iterable[_Union[APIToken, _Mapping]]] = ...) -> None: ...

class UpdateAPITokenStatusRequest(_message.Message):
    __slots__ = ("id", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: APITokenStatus
    def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[APITokenStatus, str]] = ...) -> None: ...

class UpdateAPITokenStatusResponse(_message.Message):
    __slots__ = ("id", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: APITokenStatus
    def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[APITokenStatus, str]] = ...) -> None: ...
