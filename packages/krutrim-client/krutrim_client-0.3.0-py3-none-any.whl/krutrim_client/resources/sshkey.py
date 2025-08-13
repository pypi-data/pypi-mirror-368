from __future__ import annotations

from typing_extensions import Literal

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven, NoneType
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from ..types.sshkey import sshkey_create_params
from .._resource import SyncAPIResource, AsyncAPIResource
from .._base_client import make_request_options

from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)

from ..types.sshkey.sshkey_create_response import SshkeyCreateResponse
from ..types.sshkey.sshkey_retrieve_response import SshkeyRetrieveResponse

__all__ = ["SshkeysResource", "AsyncSshkeysResource"]


class SshkeysResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SshkeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        """
        return SshkeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SshkeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        """
        return SshkeysResourceWithStreamingResponse(self)

    def create_sshkey(
        self,
        *,
        key_name: str,
        public_key: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SshkeyCreateResponse:
        """Add a new SSH key

        Args:
          key_name: The name for the SSH key.

        Must be unique.

          public_key: The actual public SSH key string (e.g., starting with "ssh-rsa").

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/v1/sshkeys",
            body=maybe_transform(
                {
                    "key_name": key_name,
                    "public_key": public_key,
                },
                sshkey_create_params.SshkeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SshkeyCreateResponse,
        )

    def retrieve_sshkey(
        self,
        ssh_key_identifier: str,
        x_region: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SshkeyRetrieveResponse:
        """
        Fetch an SSH key by its unique identifier

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not ssh_key_identifier:
            raise ValueError(f"Expected a non-empty value for `ssh_key_identifier` but received {ssh_key_identifier!r}")
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._get(
            f"/v1/sshkeys/{ssh_key_identifier}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SshkeyRetrieveResponse,
        )

    def delete_sshkey(
        self,
        ssh_key_identifier: str,
        *,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a specific SSH key by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not ssh_key_identifier:
            raise ValueError(f"Expected a non-empty value for `ssh_key_identifier` but received {ssh_key_identifier!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers.update({"x-region": x_region})
        return self._delete(
            f"/v1/sshkeys/{ssh_key_identifier}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

class AsyncSshkeysResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSshkeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        """
        return AsyncSshkeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSshkeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.
        """
        return AsyncSshkeysResourceWithStreamingResponse(self)

    async def create_sshkey(
        self,
        *,
        key_name: str,
        public_key: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SshkeyCreateResponse:
        """Add a new SSH key

        Args:
          key_name: The name for the SSH key.

        Must be unique.

          public_key: The actual public SSH key string (e.g., starting with "ssh-rsa").

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/v1/sshkeys",
            body=await async_maybe_transform(
                {
                    "key_name": key_name,
                    "public_key": public_key,
                },
                sshkey_create_params.SshkeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SshkeyCreateResponse,
        )
    
    async def retrieve_sshkey(
        self,
        ssh_key_identifier: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SshkeyRetrieveResponse:
        """
        Fetch an SSH key by its unique identifier

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not ssh_key_identifier:
            raise ValueError(f"Expected a non-empty value for `ssh_key_identifier` but received {ssh_key_identifier!r}")
        return await self._get(
            f"/v1/sshkeys/{ssh_key_identifier}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SshkeyRetrieveResponse,
        )

    async def delete_sshkey(
        self,
        ssh_key_identifier: str,
        *,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a specific SSH key by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not ssh_key_identifier:
            raise ValueError(f"Expected a non-empty value for `ssh_key_identifier` but received {ssh_key_identifier!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers.update({"x-region": x_region})
        return await self._delete(
            f"/v1/sshkeys/{ssh_key_identifier}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class SshkeysResourceWithRawResponse:
    def __init__(self, sshkeys: SshkeysResource) -> None:
        self._sshkeys = sshkeys

        self.create_sshkey = to_raw_response_wrapper(
            sshkeys.create_sshkey,
        )
        self.retrieve_sshkey = to_raw_response_wrapper(
            sshkeys.retrieve_sshkey,
        )
        self.delete_sshkey = to_raw_response_wrapper(
            sshkeys.delete_sshkey,
        )

class AsyncSshkeysResourceWithRawResponse:
    def __init__(self, sshkeys: AsyncSshkeysResource) -> None:
        self._sshkeys = sshkeys

        self.create_sshkey = async_to_raw_response_wrapper(
            sshkeys.create_sshkey,
        )
        self.retrieve_sshkey = async_to_raw_response_wrapper(
            sshkeys.retrieve_sshkey,
        )
        self.delete_sshkey = async_to_raw_response_wrapper(
            sshkeys.delete_sshkey,
        )

class SshkeysResourceWithStreamingResponse:
    def __init__(self, sshkeys: SshkeysResource) -> None:
        self._sshkeys = sshkeys

        self.create_sshkey = to_streamed_response_wrapper(
            sshkeys.create_sshkey,
        )

        self.retrieve_sshkey = to_streamed_response_wrapper(
            sshkeys.retrieve_sshkey,
        )
        self.delete_sshkey = to_streamed_response_wrapper(
            sshkeys.delete_sshkey,
        )

class AsyncSshkeysResourceWithStreamingResponse:
    def __init__(self, sshkeys: AsyncSshkeysResource) -> None:
        self._sshkeys = sshkeys

        self.create_sshkey = async_to_streamed_response_wrapper(
            sshkeys.create_sshkey,
        )
        self.retrieve_sshkey = async_to_streamed_response_wrapper(
            sshkeys.retrieve_sshkey,
        )

        self.delete_sshkey = async_to_streamed_response_wrapper(
            sshkeys.delete_sshkey,
        )
        

