from __future__ import annotations

from typing_extensions import Literal

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from ..types.startStopVM import v1_perform_action_params
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.startStopVM.v1_perform_action_response import V1PerformActionResponse

__all__ = ["StartStopResource", "AsyncStartStopResource"]


class StartStopResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StartStopResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/start_stop-python#accessing-raw-response-data-eg-headers
        """
        return StartStopResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StartStopResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/start_stop-python#with_streaming_response
        """
        return StartStopResourceWithStreamingResponse(self)


    def validate_perform_action_parameters(
    self,
    instance_krn: str,
    action: Literal["start", "stop", "reboot"],
    x_region: str,
    extra_headers: Optional[dict] = None,
    extra_query: Optional[dict] = None,
    extra_body: Optional[dict] = None,
    timeout: Union[float, int, httpx.Timeout, None, type(NOT_GIVEN)] = None,
    ) -> None:
        if not isinstance(instance_krn, str):
            raise ValueError("'instance_krn' must be a string.")

        if action not in ("start", "stop", "reboot"):
            raise ValueError("'action' must be one of: 'start', 'stop', or 'reboot'.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")

        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")

        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")

        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

    def perform_action(
        self,
        instance_krn: str,
        *,
        action: Literal["start", "stop", "reboot"],
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> V1PerformActionResponse:
        """
        Perform an action (e.g., stop) on a VM instance

        Args:
          action: The action to perform on the VM instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not instance_krn:
            raise ValueError(f"Expected a non-empty value for `instance_krn` but received {instance_krn!r}")
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        self.validate_perform_action_parameters(
        instance_krn = instance_krn,
        action = action,
        x_region = x_region,
        extra_headers = extra_headers,
        extra_query = extra_query,
        extra_body = extra_body,
        timeout = timeout,
            )
        return self._put(
            f"/vm/v1/instance/{instance_krn}",
            body=maybe_transform({"action": action}, v1_perform_action_params.V1PerformActionParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1PerformActionResponse,
        )


class AsyncStartStopResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStartStopResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/start_stop-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStartStopResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStartStopResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/start_stop-python#with_streaming_response
        """
        return AsyncStartStopResourceWithStreamingResponse(self)

    async def validate_perform_action_parameters(
    self,
    instance_krn: str,
    action: Literal["start", "stop", "reboot"],
    x_region: str,
    extra_headers: Optional[dict] = None,
    extra_query: Optional[dict] = None,
    extra_body: Optional[dict] = None,
    timeout: Union[float, int, httpx.Timeout, None, type(NOT_GIVEN)] = None,
    ) -> None:
        if not isinstance(instance_krn, str):
            raise ValueError("'instance_krn' must be a string.")

        if action not in ("start", "stop", "reboot"):
            raise ValueError("'action' must be one of: 'start', 'stop', or 'reboot'.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")

        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")

        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")

        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")


    async def perform_action(
        self,
        instance_krn: str,
        *,
        action: Literal["start", "stop", "reboot"],
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> V1PerformActionResponse:
        """
        Perform an action (e.g., stop) on a VM instance

        Args:
          action: The action to perform on the VM instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not instance_krn:
            raise ValueError(f"Expected a non-empty value for `instance_krn` but received {instance_krn!r}")
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        await self.validate_perform_action_parameters(
        instance_krn = instance_krn,
        action = action,
        x_region = x_region,
        extra_headers = extra_headers,
        extra_query = extra_query,
        extra_body = extra_body,
        timeout = timeout,
            )
        return await self._put(
            f"/vm/v1/instance/{instance_krn}",
            body=await async_maybe_transform({"action": action}, v1_perform_action_params.V1PerformActionParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1PerformActionResponse,
        )


class StartStopResourceWithRawResponse:
    def __init__(self, StartStop: StartStopResource) -> None:
        self._StartStop = StartStop

        self.perform_action = to_raw_response_wrapper(
            StartStop.perform_action,
        )


class AsyncStartStopResourceWithRawResponse:
    def __init__(self, StartStop: AsyncStartStopResource) -> None:
        self._StartStop = StartStop

        self.perform_action = async_to_raw_response_wrapper(
            StartStop.perform_action,
        )


class StartStopResourceWithStreamingResponse:
    def __init__(self, StartStop: StartStopResource) -> None:
        self._StartStop = StartStop

        self.perform_action = to_streamed_response_wrapper(
            StartStop.perform_action,
        )


class AsyncStartStopResourceWithStreamingResponse:
    def __init__(self, StartStop: AsyncStartStopResource) -> None:
        self._StartStop = StartStop

        self.perform_action = async_to_streamed_response_wrapper(
            StartStop.perform_action,
        )
