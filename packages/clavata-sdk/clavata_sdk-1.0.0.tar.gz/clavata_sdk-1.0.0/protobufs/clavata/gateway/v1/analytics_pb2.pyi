from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SeriesType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[SeriesType]
    TEXT: _ClassVar[SeriesType]
    IMAGE: _ClassVar[SeriesType]
UNKNOWN: SeriesType
TEXT: SeriesType
IMAGE: SeriesType

class TimeBucket(_message.Message):
    __slots__ = ("timestamp", "series")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SERIES_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    series: _containers.RepeatedCompositeFieldContainer[Series]
    def __init__(self, timestamp: _Optional[int] = ..., series: _Optional[_Iterable[_Union[Series, _Mapping]]] = ...) -> None: ...

class Series(_message.Message):
    __slots__ = ("count", "type")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    count: int
    type: SeriesType
    def __init__(self, count: _Optional[int] = ..., type: _Optional[_Union[SeriesType, str]] = ...) -> None: ...

class GetAnalyticsEvaluationsRequest(_message.Message):
    __slots__ = ("start", "timezone")
    START_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    start: _timestamp_pb2.Timestamp
    timezone: str
    def __init__(self, start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., timezone: _Optional[str] = ...) -> None: ...

class GetAnalyticsEvaluationsResponse(_message.Message):
    __slots__ = ("time_buckets",)
    TIME_BUCKETS_FIELD_NUMBER: _ClassVar[int]
    time_buckets: _containers.RepeatedCompositeFieldContainer[TimeBucket]
    def __init__(self, time_buckets: _Optional[_Iterable[_Union[TimeBucket, _Mapping]]] = ...) -> None: ...
