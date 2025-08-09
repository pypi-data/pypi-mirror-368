from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from clavata.gateway.v1 import errs_pb2 as _errs_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeploymentResponse(_message.Message):
    __slots__ = ("id", "name", "created_at", "updated_at", "policy_ids")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    POLICY_IDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    policy_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., policy_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetDeploymentRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetDeploymentResponse(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: DeploymentResponse
    def __init__(self, deployment: _Optional[_Union[DeploymentResponse, _Mapping]] = ...) -> None: ...

class ListDeploymentsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListDeploymentsResponse(_message.Message):
    __slots__ = ("deployments",)
    DEPLOYMENTS_FIELD_NUMBER: _ClassVar[int]
    deployments: _containers.RepeatedCompositeFieldContainer[DeploymentResponse]
    def __init__(self, deployments: _Optional[_Iterable[_Union[DeploymentResponse, _Mapping]]] = ...) -> None: ...

class CreateDeploymentRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class CreateDeploymentResponse(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: DeploymentResponse
    def __init__(self, deployment: _Optional[_Union[DeploymentResponse, _Mapping]] = ...) -> None: ...

class UpdateDeploymentRequest(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class UpdateDeploymentResponse(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: DeploymentResponse
    def __init__(self, deployment: _Optional[_Union[DeploymentResponse, _Mapping]] = ...) -> None: ...

class UpdatePolicyDeploymentsRequest(_message.Message):
    __slots__ = ("deployment_id", "add_policy_ids", "remove_policy_ids")
    DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ADD_POLICY_IDS_FIELD_NUMBER: _ClassVar[int]
    REMOVE_POLICY_IDS_FIELD_NUMBER: _ClassVar[int]
    deployment_id: str
    add_policy_ids: _containers.RepeatedScalarFieldContainer[str]
    remove_policy_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, deployment_id: _Optional[str] = ..., add_policy_ids: _Optional[_Iterable[str]] = ..., remove_policy_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdatePolicyDeploymentsResponse(_message.Message):
    __slots__ = ("deployment", "policy_label_conflicts")
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    POLICY_LABEL_CONFLICTS_FIELD_NUMBER: _ClassVar[int]
    deployment: DeploymentResponse
    policy_label_conflicts: _containers.RepeatedCompositeFieldContainer[_errs_pb2.PolicyLabelConflict]
    def __init__(self, deployment: _Optional[_Union[DeploymentResponse, _Mapping]] = ..., policy_label_conflicts: _Optional[_Iterable[_Union[_errs_pb2.PolicyLabelConflict, _Mapping]]] = ...) -> None: ...

class ArchiveDeploymentRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ArchiveDeploymentResponse(_message.Message):
    __slots__ = ("id", "archived_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ARCHIVED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    archived_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., archived_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
