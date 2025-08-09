import asyncio
import os
from collections.abc import AsyncIterator
from types import ModuleType
from typing import TypeVar

import grpc
from google.protobuf.message import Message
from grpc import aio as grpc_aio

from .errs import EvaluationRefusedError
from .models import (
    BaseModel,
    CreateJobRequest,
    CreateJobResponse,
    EvaluateOneRequest,
    EvaluateOneResponse,
    EvaluateRequest,
    EvaluateResponse,
    GetJobRequest,
    GetJobResponse,
    ListJobsQuery,
    ListJobsResponse,
)

try:
    from protobufs.clavata.gateway.v1 import gateway_pb2, gateway_pb2_grpc
except ImportError:
    # Fallback for local dev where protos are vendored under src/protobufs
    from sdk.src.protobufs.clavata.gateway.v1 import gateway_pb2, gateway_pb2_grpc

DEFAULT_HOST = "gateway.app.clavata.ai"
DEFAULT_PORT = 443

# Type variable used for generic response typing on _unary_invoke
TResponse = TypeVar("TResponse", bound=BaseModel)


class ClavataClient:
    """
    The ClavataClient class provides a convienient way to interact with the Clavata API.

    It provides methods for creating jobs, evaluating content, and retrieving jobs.

    A Clavata API key is required to use the SDK. You can either provide an API key to the constructor with
    the `auth_token` parameter, or set the `CLAVATA_API_KEY` environment variable. Note that if both
    are provided, the constructor value will take precedence.
    """

    _channel: grpc_aio.Channel | None = None
    _stub: gateway_pb2_grpc.GatewayServiceStub
    address: str
    _auth_token: str
    _secure: bool

    def __init__(
        self,
        *,
        host: str,
        port: int,
        auth_token: str | None = None,
        secure: bool = True,
    ):
        auth_token = auth_token or os.environ.get("CLAVATA_API_KEY")
        if not auth_token:
            raise ValueError(
                "No auth token provided. Please provide an auth token or set the CLAVATA_API_KEY environment variable."
            )

        self.address = f"{host}:{port}"
        self._auth_token = auth_token
        self._secure = secure

    @classmethod
    def create(cls, auth_token: str | None = None) -> "ClavataClient":
        """
        Create will create a ClavataClient ready for use with Clavata's production services.

        You can optionally provide an auth_token directly, or it will be loaded from the CLAVATA_API_KEY
        environment variable.
        """
        return ClavataClient(
            host=DEFAULT_HOST, port=DEFAULT_PORT, auth_token=auth_token, secure=True
        )

    async def connect(self):
        """Establishes the gRPC channel and creates the service stub"""

        if self._channel:
            return

        # Check whether we're using a secure channel or not, and set the channel accordingly
        self._channel = (
            grpc.aio.insecure_channel(self.address)
            if not self._secure
            else grpc_aio.secure_channel(self.address, grpc.ssl_channel_credentials())
        )
        self._stub = gateway_pb2_grpc.GatewayServiceStub(self._channel)

    async def close(self):
        """Closes the gRPC channel"""
        if not self._channel:
            return
        await self._channel.close()
        self._channel = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        # We won't handle any exceptions here, so they will propogate
        # and will need to be handled by the caller
        await self.close()

    async def _unary_invoke(
        self,
        method: str,
        request: Message,
        response_type: type["TResponse"],
        timeout: float | None = None,
    ) -> "TResponse":
        """
        Invokes a method with the given request and timeout. This helper provides us with a way
        to handle injecting the metadata and timeout into the call. We can also add any common error
        handling here in the future.
        """
        await self.connect()
        call_method = getattr(self._stub, method)
        try:
            resp = await call_method(request, metadata=self._metadata, timeout=timeout)
            return response_type.from_proto(resp)
        except grpc_aio.AioRpcError as e:
            raise EvaluationRefusedError.from_rpc_error(e) from e

    async def create_job(
        self, *, request: CreateJobRequest, timeout: float | None = None
    ) -> CreateJobResponse:
        """
        Create a new content evaluation job. A job will evaluate N pieces of content against a single
        policy. The "create_job" method is "synchronous", meaning that the request will block until
        all N pieces of content have been evaluated. The results for all N pieces of content are then
        returned in the response.

        Typical usage is as follows:

        ```python
        async with ClavataClient(host="localhost", port=50051, auth_token="...") as client:
            response = await client.create_job(request=CreateJobRequest(
                policy="...",
                content=[
                    ContentData(text="..."),
                    ContentData(text="..."),
                ],
            ))
        ```

        If you only have a single piece of content to evaluate, you can pass in a single ContentData
        object instead of a list. Like so:

        ```python
        async with ClavataClient(host="localhost", port=50051, auth_token="...") as client:
            response = await client.create_job(request=CreateJobRequest(
                policy="...",
                content=ContentData(text="..."),
            ))
        ```
        """
        return await self._unary_invoke(
            "CreateJob", request.to_proto(), CreateJobResponse, timeout=timeout
        )

    async def evaluate_one(
        self, *, request: EvaluateOneRequest, timeout: float | None = None
    ) -> EvaluateOneResponse:
        """
        Evaluate a single piece of content against a single policy. This is just a helpful wrapper
        for times when you only intend to evaluate a single piece of content.

        The benefit is that you will only get back a single evaluation report, avoiding the need for extra checks
        or needing to dig into the array for a single report.
        """
        return await self._unary_invoke(
            "CreateJob", request.to_proto(), EvaluateOneResponse, timeout
        )

    async def evaluate(
        self,
        *,
        request: EvaluateRequest,
        message_timeout: float | None = None,
        stream_timeout: float | None = None,
    ) -> AsyncIterator[EvaluateResponse]:
        """
        Evaluate N pieces of content against a single policy. One message will be sent over the
        stream for each piece of content.

        Pass an EvaluateRequest object to this method. You can construct an EvaluateRequest object
        like so:

        ```python
        request = EvaluateRequest(
            content=[ContentData(text="..."), ContentData(text="...")],
            policy_id="...",
            include_evaluation_report=True,
        )
        ```

        If you only have a single piece of content to evaluate, you can pass in a single ContentData
        object instead of a list. Like so:

        ```python
        request = EvaluateRequest(
            content=ContentData(text="..."),
            policy_id="...",
            include_evaluation_report=True,
        )
        ```

        The result of calling this method is an async iterator. As such, you can use it in an async
        for loop, or with asyncio.wait. The most common way to use this is to do:

        ```python
        async for response in client.evaluate(request):
            print(response)
        ```

        If, for some reason, you need finer grained control, you can manually await each message as
        it arrives from the iterator. Like so:

        ```python aiter = client.evaluate(request) while True:
            try:
                response = await anext(aiter) print(response)
            except StopAsyncIteration:
                break
        ```

        ### Timeouts:

        The evaluate method supports two types of timeouts.

        - `message_timeout`: This sets a max time between messages arriving. In this case, set
          `stream_timeout` to None. (We recommend setting this to 10 seconds initially and tuning as
          needed.)
        - `stream_timeout`: This sets a max time for the entire stream. In this case, set
          `message_timeout` to None.
        """
        await self.connect()

        try:
            stream: grpc_aio.UnaryStreamCall[
                gateway_pb2.EvaluateRequest, gateway_pb2.EvaluateResponse
            ] = self._stub.Evaluate(
                request.to_proto(), metadata=self._metadata, timeout=stream_timeout
            )

            # Get an async iterator from the stream. We'll use it to read each message from the stream.
            # This approach also allows us to enforce a per-message timeout using asyncio.wait_for.
            iterator = aiter(stream)
            while True:
                try:
                    # If `message_timeout` is None, no message timeout will be enforced.
                    response = await asyncio.wait_for(anext(iterator), timeout=message_timeout)
                except StopAsyncIteration:
                    # Normal termination of the stream when complete
                    break
                except TimeoutError:
                    # We've timed out on a message, so we need to cancel the stream. We'll also re-raise
                    # in case the caller wants to handle the timeout error.
                    stream.cancel()
                    raise
                else:
                    # Yield the response to the caller
                    yield EvaluateResponse.from_proto(response)
        except grpc_aio.AioRpcError as e:
            raise EvaluationRefusedError.from_rpc_error(e) from e
        except TimeoutError:
            stream.cancel()
            raise

    async def list_jobs(
        self, *, request: ListJobsQuery, timeout: float | None = None
    ) -> ListJobsResponse:
        """
        List all jobs for the current user.
        """
        return await self._unary_invoke(
            "ListJobs", request.to_proto(), ListJobsResponse, timeout=timeout
        )

    async def get_job(
        self, *, request: GetJobRequest, timeout: float | None = None
    ) -> GetJobResponse:
        """
        Get a single job using its UUID. If the job is not complete, the status will still be returned.
        """
        return await self._unary_invoke(
            "GetJob", request.to_proto(), GetJobResponse, timeout=timeout
        )

    @property
    def _metadata(self) -> tuple[tuple[str, str], ...]:
        """Creates metadata with authorization token"""
        return (("authorization", f"Bearer {self._auth_token}"),)
