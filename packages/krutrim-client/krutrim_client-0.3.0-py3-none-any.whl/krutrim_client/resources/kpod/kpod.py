from __future__ import annotations

from .pod import (
    PodResource,
    AsyncPodResource,
    PodResourceWithRawResponse,
    AsyncPodResourceWithRawResponse,
    PodResourceWithStreamingResponse,
    AsyncPodResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["KpodResource", "AsyncKpodResource"]


class KpodResource(SyncAPIResource):
    @cached_property
    def pod(self) -> PodResource:
        return PodResource(self._client)

    @cached_property
    def with_raw_response(self) -> KpodResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/kpod-python#accessing-raw-response-data-eg-headers
        """
        return KpodResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> KpodResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/kpod-python#with_streaming_response
        """
        return KpodResourceWithStreamingResponse(self)


class AsyncKpodResource(AsyncAPIResource):
    @cached_property
    def pod(self) -> AsyncPodResource:
        return AsyncPodResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncKpodResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/kpod-python#accessing-raw-response-data-eg-headers
        """
        return AsyncKpodResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncKpodResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/kpod-python#with_streaming_response
        """
        return AsyncKpodResourceWithStreamingResponse(self)


class KpodResourceWithRawResponse:
    def __init__(self, kpod: KpodResource) -> None:
        self._kpod = kpod

    @cached_property
    def pod(self) -> PodResourceWithRawResponse:
        return PodResourceWithRawResponse(self._kpod.pod)


class AsyncKpodResourceWithRawResponse:
    def __init__(self, kpod: AsyncKpodResource) -> None:
        self._kpod = kpod

    @cached_property
    def pod(self) -> AsyncPodResourceWithRawResponse:
        return AsyncPodResourceWithRawResponse(self._kpod.pod)


class KpodResourceWithStreamingResponse:
    def __init__(self, kpod: KpodResource) -> None:
        self._kpod = kpod

    @cached_property
    def pod(self) -> PodResourceWithStreamingResponse:
        return PodResourceWithStreamingResponse(self._kpod.pod)


class AsyncKpodResourceWithStreamingResponse:
    def __init__(self, kpod: AsyncKpodResource) -> None:
        self._kpod = kpod

    @cached_property
    def pod(self) -> AsyncPodResourceWithStreamingResponse:
        return AsyncPodResourceWithStreamingResponse(self._kpod.pod)
