from clavata.shared.v1 import public_pb2 as _public_pb2
from clavata.shared.v1 import shared_pb2 as _shared_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListDatasetsRequest(_message.Message):
    __slots__ = ("include_public",)
    INCLUDE_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    include_public: bool
    def __init__(self, include_public: bool = ...) -> None: ...

class ListDatasetsResponse(_message.Message):
    __slots__ = ("datasets",)
    class Dataset(_message.Message):
        __slots__ = ("dataset_id", "name", "notes", "public", "created", "updated")
        DATASET_ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        NOTES_FIELD_NUMBER: _ClassVar[int]
        PUBLIC_FIELD_NUMBER: _ClassVar[int]
        CREATED_FIELD_NUMBER: _ClassVar[int]
        UPDATED_FIELD_NUMBER: _ClassVar[int]
        dataset_id: str
        name: str
        notes: str
        public: bool
        created: _timestamp_pb2.Timestamp
        updated: _timestamp_pb2.Timestamp
        def __init__(self, dataset_id: _Optional[str] = ..., name: _Optional[str] = ..., notes: _Optional[str] = ..., public: bool = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    datasets: _containers.RepeatedCompositeFieldContainer[ListDatasetsResponse.Dataset]
    def __init__(self, datasets: _Optional[_Iterable[_Union[ListDatasetsResponse.Dataset, _Mapping]]] = ...) -> None: ...

class CreateDatasetRequest(_message.Message):
    __slots__ = ("name", "notes")
    NAME_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    name: str
    notes: str
    def __init__(self, name: _Optional[str] = ..., notes: _Optional[str] = ...) -> None: ...

class CreateDatasetResponse(_message.Message):
    __slots__ = ("dataset_id",)
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    def __init__(self, dataset_id: _Optional[str] = ...) -> None: ...

class AppendContentToDatasetRequest(_message.Message):
    __slots__ = ("dataset_id", "content_with_labels", "bulk_labels")
    class ContentWithLabels(_message.Message):
        __slots__ = ("customer_content_id", "labels")
        CUSTOMER_CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
        LABELS_FIELD_NUMBER: _ClassVar[int]
        customer_content_id: str
        labels: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, customer_content_id: _Optional[str] = ..., labels: _Optional[_Iterable[str]] = ...) -> None: ...
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_WITH_LABELS_FIELD_NUMBER: _ClassVar[int]
    BULK_LABELS_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    content_with_labels: _containers.RepeatedCompositeFieldContainer[AppendContentToDatasetRequest.ContentWithLabels]
    bulk_labels: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, dataset_id: _Optional[str] = ..., content_with_labels: _Optional[_Iterable[_Union[AppendContentToDatasetRequest.ContentWithLabels, _Mapping]]] = ..., bulk_labels: _Optional[_Iterable[str]] = ...) -> None: ...

class AppendContentToDatasetResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class AppendApiContentToDatasetRequest(_message.Message):
    __slots__ = ("dataset_id", "content_hashes_with_labels", "override_labels")
    class ContentHashWithLabels(_message.Message):
        __slots__ = ("content_hash", "labels")
        CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
        LABELS_FIELD_NUMBER: _ClassVar[int]
        content_hash: str
        labels: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, content_hash: _Optional[str] = ..., labels: _Optional[_Iterable[str]] = ...) -> None: ...
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASHES_WITH_LABELS_FIELD_NUMBER: _ClassVar[int]
    OVERRIDE_LABELS_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    content_hashes_with_labels: _containers.RepeatedCompositeFieldContainer[AppendApiContentToDatasetRequest.ContentHashWithLabels]
    override_labels: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, dataset_id: _Optional[str] = ..., content_hashes_with_labels: _Optional[_Iterable[_Union[AppendApiContentToDatasetRequest.ContentHashWithLabels, _Mapping]]] = ..., override_labels: _Optional[_Iterable[str]] = ...) -> None: ...

class AppendApiContentToDatasetResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ListDatasetContentRequest(_message.Message):
    __slots__ = ("dataset_id", "query")
    class Query(_message.Message):
        __slots__ = ("labels", "content_modalities", "content")
        LABELS_FIELD_NUMBER: _ClassVar[int]
        CONTENT_MODALITIES_FIELD_NUMBER: _ClassVar[int]
        CONTENT_FIELD_NUMBER: _ClassVar[int]
        labels: _containers.RepeatedScalarFieldContainer[str]
        content_modalities: _containers.RepeatedScalarFieldContainer[_shared_pb2.ContentModality]
        content: str
        def __init__(self, labels: _Optional[_Iterable[str]] = ..., content_modalities: _Optional[_Iterable[_Union[_shared_pb2.ContentModality, str]]] = ..., content: _Optional[str] = ...) -> None: ...
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    query: ListDatasetContentRequest.Query
    def __init__(self, dataset_id: _Optional[str] = ..., query: _Optional[_Union[ListDatasetContentRequest.Query, _Mapping]] = ...) -> None: ...

class ListDatasetContentResponse(_message.Message):
    __slots__ = ("items",)
    class DatasetItem(_message.Message):
        __slots__ = ("id", "dataset_id", "customer_content_id")
        ID_FIELD_NUMBER: _ClassVar[int]
        DATASET_ID_FIELD_NUMBER: _ClassVar[int]
        CUSTOMER_CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
        id: str
        dataset_id: str
        customer_content_id: str
        def __init__(self, id: _Optional[str] = ..., dataset_id: _Optional[str] = ..., customer_content_id: _Optional[str] = ...) -> None: ...
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[ListDatasetContentResponse.DatasetItem]
    def __init__(self, items: _Optional[_Iterable[_Union[ListDatasetContentResponse.DatasetItem, _Mapping]]] = ...) -> None: ...

class GetDatasetContentRequest(_message.Message):
    __slots__ = ("dataset_id", "dataset_item_ids")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_ITEM_IDS_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    dataset_item_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, dataset_id: _Optional[str] = ..., dataset_item_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetDatasetContentResponse(_message.Message):
    __slots__ = ("contents",)
    class ExtendedContentData(_message.Message):
        __slots__ = ("customer_content_id", "dataset_item_id", "content_data")
        CUSTOMER_CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
        DATASET_ITEM_ID_FIELD_NUMBER: _ClassVar[int]
        CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
        customer_content_id: str
        dataset_item_id: str
        content_data: _public_pb2.ContentData
        def __init__(self, customer_content_id: _Optional[str] = ..., dataset_item_id: _Optional[str] = ..., content_data: _Optional[_Union[_public_pb2.ContentData, _Mapping]] = ...) -> None: ...
    CONTENTS_FIELD_NUMBER: _ClassVar[int]
    contents: _containers.RepeatedCompositeFieldContainer[GetDatasetContentResponse.ExtendedContentData]
    def __init__(self, contents: _Optional[_Iterable[_Union[GetDatasetContentResponse.ExtendedContentData, _Mapping]]] = ...) -> None: ...

class DeleteDatasetRequest(_message.Message):
    __slots__ = ("dataset_ids",)
    DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    dataset_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, dataset_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteDatasetResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class RemoveFromDatasetRequest(_message.Message):
    __slots__ = ("dataset_id", "dataset_item_ids")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_ITEM_IDS_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    dataset_item_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, dataset_id: _Optional[str] = ..., dataset_item_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class RemoveFromDatasetResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ListDatasetLabelsRequest(_message.Message):
    __slots__ = ("dataset_id",)
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    def __init__(self, dataset_id: _Optional[str] = ...) -> None: ...

class ListDatasetLabelsResponse(_message.Message):
    __slots__ = ("labels",)
    LABELS_FIELD_NUMBER: _ClassVar[int]
    labels: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, labels: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateDatasetItemLabelsRequest(_message.Message):
    __slots__ = ("dataset_id", "dataset_item_ids", "labels")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_ITEM_IDS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    dataset_item_ids: _containers.RepeatedScalarFieldContainer[str]
    labels: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, dataset_id: _Optional[str] = ..., dataset_item_ids: _Optional[_Iterable[str]] = ..., labels: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateDatasetItemLabelsResponse(_message.Message):
    __slots__ = ("dataset_item_ids",)
    DATASET_ITEM_IDS_FIELD_NUMBER: _ClassVar[int]
    dataset_item_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, dataset_item_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateDatasetRequest(_message.Message):
    __slots__ = ("dataset_id", "name", "notes")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    name: str
    notes: str
    def __init__(self, dataset_id: _Optional[str] = ..., name: _Optional[str] = ..., notes: _Optional[str] = ...) -> None: ...

class UpdateDatasetResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ClonePublicDatasetToAccountRequest(_message.Message):
    __slots__ = ("source_dataset_id", "cloned_dataset_name")
    SOURCE_DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    CLONED_DATASET_NAME_FIELD_NUMBER: _ClassVar[int]
    source_dataset_id: str
    cloned_dataset_name: str
    def __init__(self, source_dataset_id: _Optional[str] = ..., cloned_dataset_name: _Optional[str] = ...) -> None: ...

class ClonePublicDatasetToAccountResponse(_message.Message):
    __slots__ = ("dataset_id", "source_dataset_id")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    source_dataset_id: str
    def __init__(self, dataset_id: _Optional[str] = ..., source_dataset_id: _Optional[str] = ...) -> None: ...
