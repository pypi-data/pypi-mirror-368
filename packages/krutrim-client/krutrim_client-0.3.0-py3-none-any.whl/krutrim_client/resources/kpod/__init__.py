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

__all__ = [
    "PodResource",
    "AsyncPodResource",
    "PodResourceWithRawResponse",
    "AsyncPodResourceWithRawResponse",
    "PodResourceWithStreamingResponse",
    "AsyncPodResourceWithStreamingResponse",
    "KpodResource",
    "AsyncKpodResource",
    "KpodResourceWithRawResponse",
    "AsyncKpodResourceWithRawResponse",
    "KpodResourceWithStreamingResponse",
    "AsyncKpodResourceWithStreamingResponse",
]


class KpodResource(SyncAPIResource):
    @cached_property
    def pod(self) -> PodResource:
        return PodResource(self._client)


class AsyncKpodResource(AsyncAPIResource):
    @cached_property
    def pod(self) -> AsyncPodResource:
        return AsyncPodResource(self._client)


class KpodResourceWithRawResponse:
    def __init__(self, kpod: KpodResource) -> None:
        self.pod = PodResourceWithRawResponse(kpod.pod)


class AsyncKpodResourceWithRawResponse:
    def __init__(self, kpod: AsyncKpodResource) -> None:
        self.pod = AsyncPodResourceWithRawResponse(kpod.pod)


class KpodResourceWithStreamingResponse:
    def __init__(self, kpod: KpodResource) -> None:
        self.pod = PodResourceWithStreamingResponse(kpod.pod)


class AsyncKpodResourceWithStreamingResponse:
    def __init__(self, kpod: AsyncKpodResource) -> None:
        self.pod = AsyncPodResourceWithStreamingResponse(kpod.pod)