from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCustomerReviewLimitRequest(_message.Message):
    __slots__ = ("customer_id",)
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    def __init__(self, customer_id: _Optional[str] = ...) -> None: ...

class GetCustomerReviewLimitResponse(_message.Message):
    __slots__ = ("limit", "originalLimit")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    ORIGINALLIMIT_FIELD_NUMBER: _ClassVar[int]
    limit: int
    originalLimit: int
    def __init__(self, limit: _Optional[int] = ..., originalLimit: _Optional[int] = ...) -> None: ...

class UpdateCustomerReviewLimitRequest(_message.Message):
    __slots__ = ("customer_id", "limit")
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    limit: int
    def __init__(self, customer_id: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class UpdateCustomerReviewLimitResponse(_message.Message):
    __slots__ = ("limit",)
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    limit: int
    def __init__(self, limit: _Optional[int] = ...) -> None: ...

class RateLimit(_message.Message):
    __slots__ = ("limit", "burst", "period")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    BURST_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    limit: int
    burst: int
    period: _duration_pb2.Duration
    def __init__(self, limit: _Optional[int] = ..., burst: _Optional[int] = ..., period: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class ListRateLimitsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListRateLimitsResponse(_message.Message):
    __slots__ = ("buckets",)
    BUCKETS_FIELD_NUMBER: _ClassVar[int]
    buckets: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, buckets: _Optional[_Iterable[str]] = ...) -> None: ...

class GetCustomerRateLimitsRequest(_message.Message):
    __slots__ = ("customer_id", "buckets")
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    BUCKETS_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    buckets: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, customer_id: _Optional[str] = ..., buckets: _Optional[_Iterable[str]] = ...) -> None: ...

class GetCustomerRateLimitsResponse(_message.Message):
    __slots__ = ("rate_limits",)
    class RateLimitsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: RateLimit
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[RateLimit, _Mapping]] = ...) -> None: ...
    RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    rate_limits: _containers.MessageMap[str, RateLimit]
    def __init__(self, rate_limits: _Optional[_Mapping[str, RateLimit]] = ...) -> None: ...

class UpdateCustomerRateLimitsRequest(_message.Message):
    __slots__ = ("customer_id", "rate_limits")
    class RateLimitsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: RateLimit
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[RateLimit, _Mapping]] = ...) -> None: ...
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    rate_limits: _containers.MessageMap[str, RateLimit]
    def __init__(self, customer_id: _Optional[str] = ..., rate_limits: _Optional[_Mapping[str, RateLimit]] = ...) -> None: ...

class UpdateCustomerRateLimitsResponse(_message.Message):
    __slots__ = ("rate_limits",)
    class RateLimitsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: RateLimit
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[RateLimit, _Mapping]] = ...) -> None: ...
    RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    rate_limits: _containers.MessageMap[str, RateLimit]
    def __init__(self, rate_limits: _Optional[_Mapping[str, RateLimit]] = ...) -> None: ...
