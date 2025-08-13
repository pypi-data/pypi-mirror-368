from __future__ import annotations

from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

from .accessKeys import (
    AccessKeysResource,
    AsyncAccessKeysResource,
    AccessKeysResourceWithRawResponse,
    AsyncAccessKeysResourceWithRawResponse,
    AccessKeysResourceWithStreamingResponse,
    AsyncAccessKeysResourceWithStreamingResponse,
)

from .buckets import (
    BucketsResource,
    AsyncBucketsResource,
    BucketsResourceWithRawResponse,
    AsyncBucketsResourceWithRawResponse,
    BucketsResourceWithStreamingResponse,
    AsyncBucketsResourceWithStreamingResponse,
)


__all__ = ["KosResource", "AsyncKosResource"]


class KosResource(SyncAPIResource):
    @cached_property
    def accessKeys(self) -> AccessKeysResource:
        return AccessKeysResource(self._client)

    @cached_property
    def buckets(self) -> BucketsResource:
        return BucketsResource(self._client)
    

    @cached_property
    def with_raw_response(self) -> KosResourceWithRawResponse:
        return KosResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> KosResourceWithStreamingResponse:
        return KosResourceWithStreamingResponse(self)


class AsyncKosResource(AsyncAPIResource):
    @cached_property
    def accessKeys(self) -> AsyncAccessKeysResource:
        return AsyncAccessKeysResource(self._client)

    @cached_property
    def buckets(self) -> AsyncBucketsResource:
        return AsyncBucketsResource(self._client)
 

    @cached_property
    def with_raw_response(self) -> AsyncKosResourceWithRawResponse:
        return AsyncKosResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncKosResourceWithStreamingResponse:
        return AsyncKosResourceWithStreamingResponse(self)


# -------- Raw Response Wrappers -------- #

class KosResourceWithRawResponse:
    def __init__(self, kos: KosResource) -> None:
        self._kos = kos

    @cached_property
    def accessKeys(self) -> AccessKeysResourceWithRawResponse:
        return AccessKeysResourceWithRawResponse(self._kos.accessKeys)

    @cached_property
    def buckets(self) -> BucketsResourceWithRawResponse:
        return BucketsResourceWithRawResponse(self._kos.buckets)

   


class AsyncKosResourceWithRawResponse:
    def __init__(self, kos: AsyncKosResource) -> None:
        self._kos = kos

    @cached_property
    def accessKeys(self) -> AsyncAccessKeysResourceWithRawResponse:
        return AsyncAccessKeysResourceWithRawResponse(self._kos.accessKeys)

    @cached_property
    def buckets(self) -> AsyncBucketsResourceWithRawResponse:
        return AsyncBucketsResourceWithRawResponse(self._kos.buckets)
   
    


# -------- Streaming Response Wrappers -------- #

class KosResourceWithStreamingResponse:
    def __init__(self, kos: KosResource) -> None:
        self._kos = kos

    @cached_property
    def accessKeys(self) -> AccessKeysResourceWithStreamingResponse:
        return AccessKeysResourceWithStreamingResponse(self._kos.accessKeys)

    @cached_property
    def buckets(self) -> BucketsResourceWithStreamingResponse:
        return BucketsResourceWithStreamingResponse(self._kos.buckets)
  


class AsyncKosResourceWithStreamingResponse:
    def __init__(self, kos: AsyncKosResource) -> None:
        self._kos = kos

    @cached_property
    def accessKeys(self) -> AsyncAccessKeysResourceWithStreamingResponse:
        return AsyncAccessKeysResourceWithStreamingResponse(self._kos.accessKeys)

    @cached_property
    def buckets(self) -> AsyncBucketsResourceWithStreamingResponse:
        return AsyncBucketsResourceWithStreamingResponse(self._kos.buckets)
    
