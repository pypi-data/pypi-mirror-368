from clavata.shared.v1 import public_pb2 as _public_pb2
from clavata.shared.v1 import shared_pb2 as _shared_pb2
from google.protobuf import field_mask_pb2 as _field_mask_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FailureStage(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FAILURE_STAGE_CONTENT_PROCESSING: _ClassVar[FailureStage]
    FAILURE_STAGE_PRECHECKS: _ClassVar[FailureStage]
    FAILURE_STAGE_ASYNC_PRECHECKS: _ClassVar[FailureStage]
    FAILURE_STAGE_DATABASE: _ClassVar[FailureStage]
FAILURE_STAGE_CONTENT_PROCESSING: FailureStage
FAILURE_STAGE_PRECHECKS: FailureStage
FAILURE_STAGE_ASYNC_PRECHECKS: FailureStage
FAILURE_STAGE_DATABASE: FailureStage

class AddToCustomerContentRequest(_message.Message):
    __slots__ = ("content_data", "labels")
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    content_data: _containers.RepeatedCompositeFieldContainer[_public_pb2.ContentData]
    labels: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, content_data: _Optional[_Iterable[_Union[_public_pb2.ContentData, _Mapping]]] = ..., labels: _Optional[_Iterable[str]] = ...) -> None: ...

class AddToCustomerContentResponse(_message.Message):
    __slots__ = ("successful_content", "failed_content", "summary")
    SUCCESSFUL_CONTENT_FIELD_NUMBER: _ClassVar[int]
    FAILED_CONTENT_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    successful_content: _containers.RepeatedCompositeFieldContainer[SuccessfulContent]
    failed_content: _containers.RepeatedCompositeFieldContainer[FailedContent]
    summary: BatchSummary
    def __init__(self, successful_content: _Optional[_Iterable[_Union[SuccessfulContent, _Mapping]]] = ..., failed_content: _Optional[_Iterable[_Union[FailedContent, _Mapping]]] = ..., summary: _Optional[_Union[BatchSummary, _Mapping]] = ...) -> None: ...

class SuccessfulContent(_message.Message):
    __slots__ = ("customer_content_id", "original_index")
    CUSTOMER_CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_INDEX_FIELD_NUMBER: _ClassVar[int]
    customer_content_id: str
    original_index: int
    def __init__(self, customer_content_id: _Optional[str] = ..., original_index: _Optional[int] = ...) -> None: ...

class FailedContent(_message.Message):
    __slots__ = ("original_index", "stage", "error_message", "error_code")
    ORIGINAL_INDEX_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    original_index: int
    stage: FailureStage
    error_message: str
    error_code: str
    def __init__(self, original_index: _Optional[int] = ..., stage: _Optional[_Union[FailureStage, str]] = ..., error_message: _Optional[str] = ..., error_code: _Optional[str] = ...) -> None: ...

class BatchSummary(_message.Message):
    __slots__ = ("successful_count", "failed_count")
    SUCCESSFUL_COUNT_FIELD_NUMBER: _ClassVar[int]
    FAILED_COUNT_FIELD_NUMBER: _ClassVar[int]
    successful_count: int
    failed_count: int
    def __init__(self, successful_count: _Optional[int] = ..., failed_count: _Optional[int] = ...) -> None: ...

class GetCustomerContentRequest(_message.Message):
    __slots__ = ("customer_content_ids",)
    CUSTOMER_CONTENT_IDS_FIELD_NUMBER: _ClassVar[int]
    customer_content_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, customer_content_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetCustomerContentResponse(_message.Message):
    __slots__ = ("contents",)
    class ExtendedContentData(_message.Message):
        __slots__ = ("customer_content_id", "content_data")
        CUSTOMER_CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
        CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
        customer_content_id: str
        content_data: _public_pb2.ContentData
        def __init__(self, customer_content_id: _Optional[str] = ..., content_data: _Optional[_Union[_public_pb2.ContentData, _Mapping]] = ...) -> None: ...
    CONTENTS_FIELD_NUMBER: _ClassVar[int]
    contents: _containers.RepeatedCompositeFieldContainer[GetCustomerContentResponse.ExtendedContentData]
    def __init__(self, contents: _Optional[_Iterable[_Union[GetCustomerContentResponse.ExtendedContentData, _Mapping]]] = ...) -> None: ...

class DeleteFromCustomerContentRequest(_message.Message):
    __slots__ = ("customer_content_ids",)
    CUSTOMER_CONTENT_IDS_FIELD_NUMBER: _ClassVar[int]
    customer_content_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, customer_content_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteFromCustomerContentResponse(_message.Message):
    __slots__ = ("customer_content_ids", "conflicts")
    class DatasetConflictValue(_message.Message):
        __slots__ = ("dataset_id", "name")
        DATASET_ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        dataset_id: str
        name: str
        def __init__(self, dataset_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...
    class DatasetConflict(_message.Message):
        __slots__ = ("customer_content_id", "datasets")
        CUSTOMER_CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
        DATASETS_FIELD_NUMBER: _ClassVar[int]
        customer_content_id: str
        datasets: _containers.RepeatedCompositeFieldContainer[DeleteFromCustomerContentResponse.DatasetConflictValue]
        def __init__(self, customer_content_id: _Optional[str] = ..., datasets: _Optional[_Iterable[_Union[DeleteFromCustomerContentResponse.DatasetConflictValue, _Mapping]]] = ...) -> None: ...
    CUSTOMER_CONTENT_IDS_FIELD_NUMBER: _ClassVar[int]
    CONFLICTS_FIELD_NUMBER: _ClassVar[int]
    customer_content_ids: _containers.RepeatedScalarFieldContainer[str]
    conflicts: _containers.RepeatedCompositeFieldContainer[DeleteFromCustomerContentResponse.DatasetConflict]
    def __init__(self, customer_content_ids: _Optional[_Iterable[str]] = ..., conflicts: _Optional[_Iterable[_Union[DeleteFromCustomerContentResponse.DatasetConflict, _Mapping]]] = ...) -> None: ...

class UpdateCustomerContentsRequest(_message.Message):
    __slots__ = ("updates",)
    class Body(_message.Message):
        __slots__ = ("customer_content_id", "update")
        class Update(_message.Message):
            __slots__ = ("update_mask", "title", "text", "labels")
            UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
            TITLE_FIELD_NUMBER: _ClassVar[int]
            TEXT_FIELD_NUMBER: _ClassVar[int]
            LABELS_FIELD_NUMBER: _ClassVar[int]
            update_mask: _field_mask_pb2.FieldMask
            title: str
            text: str
            labels: _containers.RepeatedScalarFieldContainer[str]
            def __init__(self, update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ..., title: _Optional[str] = ..., text: _Optional[str] = ..., labels: _Optional[_Iterable[str]] = ...) -> None: ...
        CUSTOMER_CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
        UPDATE_FIELD_NUMBER: _ClassVar[int]
        customer_content_id: str
        update: UpdateCustomerContentsRequest.Body.Update
        def __init__(self, customer_content_id: _Optional[str] = ..., update: _Optional[_Union[UpdateCustomerContentsRequest.Body.Update, _Mapping]] = ...) -> None: ...
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    updates: _containers.RepeatedCompositeFieldContainer[UpdateCustomerContentsRequest.Body]
    def __init__(self, updates: _Optional[_Iterable[_Union[UpdateCustomerContentsRequest.Body, _Mapping]]] = ...) -> None: ...

class UpdateCustomerContentsResponse(_message.Message):
    __slots__ = ("customer_content_ids",)
    CUSTOMER_CONTENT_IDS_FIELD_NUMBER: _ClassVar[int]
    customer_content_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, customer_content_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class ListCustomerContentRequest(_message.Message):
    __slots__ = ("query",)
    class Query(_message.Message):
        __slots__ = ("labels", "content_modalities", "content")
        LABELS_FIELD_NUMBER: _ClassVar[int]
        CONTENT_MODALITIES_FIELD_NUMBER: _ClassVar[int]
        CONTENT_FIELD_NUMBER: _ClassVar[int]
        labels: _containers.RepeatedScalarFieldContainer[str]
        content_modalities: _containers.RepeatedScalarFieldContainer[_shared_pb2.ContentModality]
        content: str
        def __init__(self, labels: _Optional[_Iterable[str]] = ..., content_modalities: _Optional[_Iterable[_Union[_shared_pb2.ContentModality, str]]] = ..., content: _Optional[str] = ...) -> None: ...
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: ListCustomerContentRequest.Query
    def __init__(self, query: _Optional[_Union[ListCustomerContentRequest.Query, _Mapping]] = ...) -> None: ...

class ListCustomerContentResponse(_message.Message):
    __slots__ = ("customer_content_ids",)
    CUSTOMER_CONTENT_IDS_FIELD_NUMBER: _ClassVar[int]
    customer_content_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, customer_content_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class ListCustomerContentLabelsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListCustomerContentLabelsResponse(_message.Message):
    __slots__ = ("labels",)
    LABELS_FIELD_NUMBER: _ClassVar[int]
    labels: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, labels: _Optional[_Iterable[str]] = ...) -> None: ...
