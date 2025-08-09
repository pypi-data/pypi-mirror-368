from clavata.shared.v1 import shared_pb2 as _shared_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AccountUser(_message.Message):
    __slots__ = ("user_id", "email", "role", "last_login", "first_name", "last_name")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    LAST_LOGIN_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    email: str
    role: _shared_pb2.Role
    last_login: _timestamp_pb2.Timestamp
    first_name: str
    last_name: str
    def __init__(self, user_id: _Optional[str] = ..., email: _Optional[str] = ..., role: _Optional[_Union[_shared_pb2.Role, str]] = ..., last_login: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ...) -> None: ...

class GetUserRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class GetUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: AccountUser
    def __init__(self, user: _Optional[_Union[AccountUser, _Mapping]] = ...) -> None: ...

class GetUsersRequest(_message.Message):
    __slots__ = ("query",)
    class Query(_message.Message):
        __slots__ = ("role",)
        ROLE_FIELD_NUMBER: _ClassVar[int]
        role: _shared_pb2.Role
        def __init__(self, role: _Optional[_Union[_shared_pb2.Role, str]] = ...) -> None: ...
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: GetUsersRequest.Query
    def __init__(self, query: _Optional[_Union[GetUsersRequest.Query, _Mapping]] = ...) -> None: ...

class GetUsersResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[AccountUser]
    def __init__(self, users: _Optional[_Iterable[_Union[AccountUser, _Mapping]]] = ...) -> None: ...

class PatchUserRequest(_message.Message):
    __slots__ = ("user_id", "patch")
    class Patch(_message.Message):
        __slots__ = ("role", "first_name", "last_name")
        ROLE_FIELD_NUMBER: _ClassVar[int]
        FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
        LAST_NAME_FIELD_NUMBER: _ClassVar[int]
        role: _shared_pb2.Role
        first_name: str
        last_name: str
        def __init__(self, role: _Optional[_Union[_shared_pb2.Role, str]] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ...) -> None: ...
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PATCH_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    patch: PatchUserRequest.Patch
    def __init__(self, user_id: _Optional[str] = ..., patch: _Optional[_Union[PatchUserRequest.Patch, _Mapping]] = ...) -> None: ...

class PatchUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: AccountUser
    def __init__(self, user: _Optional[_Union[AccountUser, _Mapping]] = ...) -> None: ...

class DeleteUserRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class DeleteUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: AccountUser
    def __init__(self, user: _Optional[_Union[AccountUser, _Mapping]] = ...) -> None: ...

class Customer(_message.Message):
    __slots__ = ("customer_id", "name", "email", "created_at", "updated_at", "users", "tos_accepted")
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    TOS_ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    name: str
    email: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    users: _containers.RepeatedCompositeFieldContainer[AccountUser]
    tos_accepted: bool
    def __init__(self, customer_id: _Optional[str] = ..., name: _Optional[str] = ..., email: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., users: _Optional[_Iterable[_Union[AccountUser, _Mapping]]] = ..., tos_accepted: bool = ...) -> None: ...

class ListCustomersRequest(_message.Message):
    __slots__ = ("options", "sorting")
    class Sorting(_message.Message):
        __slots__ = ("by", "order")
        BY_FIELD_NUMBER: _ClassVar[int]
        ORDER_FIELD_NUMBER: _ClassVar[int]
        by: str
        order: _shared_pb2.SortOrder
        def __init__(self, by: _Optional[str] = ..., order: _Optional[_Union[_shared_pb2.SortOrder, str]] = ...) -> None: ...
    class Options(_message.Message):
        __slots__ = ("hydrate_users",)
        HYDRATE_USERS_FIELD_NUMBER: _ClassVar[int]
        hydrate_users: bool
        def __init__(self, hydrate_users: bool = ...) -> None: ...
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SORTING_FIELD_NUMBER: _ClassVar[int]
    options: ListCustomersRequest.Options
    sorting: _containers.RepeatedCompositeFieldContainer[ListCustomersRequest.Sorting]
    def __init__(self, options: _Optional[_Union[ListCustomersRequest.Options, _Mapping]] = ..., sorting: _Optional[_Iterable[_Union[ListCustomersRequest.Sorting, _Mapping]]] = ...) -> None: ...

class ListCustomersResponse(_message.Message):
    __slots__ = ("customers",)
    CUSTOMERS_FIELD_NUMBER: _ClassVar[int]
    customers: _containers.RepeatedCompositeFieldContainer[Customer]
    def __init__(self, customers: _Optional[_Iterable[_Union[Customer, _Mapping]]] = ...) -> None: ...

class GetCustomerRequest(_message.Message):
    __slots__ = ("customer_id",)
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    def __init__(self, customer_id: _Optional[str] = ...) -> None: ...

class GetCustomerResponse(_message.Message):
    __slots__ = ("customer",)
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    customer: Customer
    def __init__(self, customer: _Optional[_Union[Customer, _Mapping]] = ...) -> None: ...

class PatchCustomerRequest(_message.Message):
    __slots__ = ("customer_id", "patch")
    class Patch(_message.Message):
        __slots__ = ("name", "email")
        NAME_FIELD_NUMBER: _ClassVar[int]
        EMAIL_FIELD_NUMBER: _ClassVar[int]
        name: str
        email: str
        def __init__(self, name: _Optional[str] = ..., email: _Optional[str] = ...) -> None: ...
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    PATCH_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    patch: PatchCustomerRequest.Patch
    def __init__(self, customer_id: _Optional[str] = ..., patch: _Optional[_Union[PatchCustomerRequest.Patch, _Mapping]] = ...) -> None: ...

class PatchCustomerResponse(_message.Message):
    __slots__ = ("customer",)
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    customer: Customer
    def __init__(self, customer: _Optional[_Union[Customer, _Mapping]] = ...) -> None: ...

class DeleteCustomerRequest(_message.Message):
    __slots__ = ("customer_id",)
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    def __init__(self, customer_id: _Optional[str] = ...) -> None: ...

class DeleteCustomerResponse(_message.Message):
    __slots__ = ("customer",)
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    customer: Customer
    def __init__(self, customer: _Optional[_Union[Customer, _Mapping]] = ...) -> None: ...

class AcceptCustomerTOSRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AcceptCustomerTOSResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
