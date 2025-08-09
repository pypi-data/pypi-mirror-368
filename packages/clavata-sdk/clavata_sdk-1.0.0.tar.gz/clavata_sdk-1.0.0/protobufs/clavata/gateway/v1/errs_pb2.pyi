from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PrecheckFailureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRECHECK_FAILURE_TYPE_UNSPECIFIED: _ClassVar[PrecheckFailureType]
    PRECHECK_FAILURE_TYPE_NCMEC: _ClassVar[PrecheckFailureType]
    PRECHECK_FAILURE_TYPE_UNSUPPORTED_IMAGE_FORMAT: _ClassVar[PrecheckFailureType]
    PRECHECK_FAILURE_TYPE_INVALID_IMAGE: _ClassVar[PrecheckFailureType]
PRECHECK_FAILURE_TYPE_UNSPECIFIED: PrecheckFailureType
PRECHECK_FAILURE_TYPE_NCMEC: PrecheckFailureType
PRECHECK_FAILURE_TYPE_UNSUPPORTED_IMAGE_FORMAT: PrecheckFailureType
PRECHECK_FAILURE_TYPE_INVALID_IMAGE: PrecheckFailureType

class PrecheckFailure(_message.Message):
    __slots__ = ("type", "message", "details")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    type: PrecheckFailureType
    message: str
    details: _struct_pb2.Value
    def __init__(self, type: _Optional[_Union[PrecheckFailureType, str]] = ..., message: _Optional[str] = ..., details: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...

class PolicyLabelConflict(_message.Message):
    __slots__ = ("label_name", "policy_ids", "deployment_id")
    LABEL_NAME_FIELD_NUMBER: _ClassVar[int]
    POLICY_IDS_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    label_name: str
    policy_ids: _containers.RepeatedScalarFieldContainer[str]
    deployment_id: str
    def __init__(self, label_name: _Optional[str] = ..., policy_ids: _Optional[_Iterable[str]] = ..., deployment_id: _Optional[str] = ...) -> None: ...

class PolicyLabelError(_message.Message):
    __slots__ = ("message", "conflicts")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CONFLICTS_FIELD_NUMBER: _ClassVar[int]
    message: str
    conflicts: _containers.RepeatedCompositeFieldContainer[PolicyLabelConflict]
    def __init__(self, message: _Optional[str] = ..., conflicts: _Optional[_Iterable[_Union[PolicyLabelConflict, _Mapping]]] = ...) -> None: ...
