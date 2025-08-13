from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.kos.accessKeys.access_keys_create_params import AccessKeyCreateParams
from ...types.kos.accessKeys.access_keys_list_response import AccessKeyListResponse
from ...types.kos.accessKeys.access_keys_create_response import AccessKeyCreateResponse




__all__ = ["AccessKeysResource", "AsyncAccessKeysResource"]


class AccessKeysResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AccessKeysResourceWithRawResponse:
       
        return AccessKeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AccessKeysResourceWithStreamingResponse:
       
        return AccessKeysResourceWithStreamingResponse(self)

    def validate_create_access_keys_params(self, *, key_name: str, region: str, x_region_id: str) -> None:
        
        if not isinstance(key_name, str) or not key_name.strip():
            raise ValueError("'key_name' must be a non-empty string.")
        if not isinstance(region, str) or not region.strip():
            raise ValueError("'region' must be a non-empty string.")
        if not isinstance(x_region_id, str) or not x_region_id.strip():
            raise ValueError("'x_region_id' must be a non-empty string.")

    def validate_delete_access_keys_params(self, *, access_key_id: str, x_region_id: str) -> None:
        if not isinstance(access_key_id, str) or not access_key_id.strip():
            raise ValueError("'access_key_id' must be a non-empty string.")
        if not isinstance(x_region_id, str) or not x_region_id.strip():
            raise ValueError("'x_region_id' must be a non-empty string.")
        
   

    def create_access_keys(
        self,
        *,
        key_name: str,
        region: str,
        x_region_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccessKeyCreateResponse:
        """
        Create a new access key

        Args:
          key_name: The name for the access key.

          region: The region associated with the access key.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_create_access_keys_params(
        key_name=key_name,
        region=region,
        x_region_id=x_region_id
        )
        extra_headers = {"x-region-id": x_region_id, **(extra_headers or {})}

        return self._post(
            "/kos/v1/access_keys",
            body=maybe_transform(
                {
                    "key_name": key_name,
                    "region": region,
                },
                AccessKeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccessKeyCreateResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccessKeyListResponse:
        """List all access keys for the current user"""
        return self._get(
            "/kos/v1/access_keys",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccessKeyListResponse,
        )

    def delete_access_keys(
        self,
        *,
        access_key_id: str,
        x_region_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> dict:
        """
        Delete an access key by its ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not access_key_id:
            raise ValueError(f"Expected a non-empty value for `access_key_id` but received {access_key_id!r}")
        self.validate_delete_access_keys_params(access_key_id=access_key_id, x_region_id=x_region_id)    
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers.update({"x-region-id": x_region_id})
        
        self._delete(
            f"/kos/v1/access_keys/{access_key_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )
        return {"access_key_id": access_key_id}


class AsyncAccessKeysResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAccessKeysResourceWithRawResponse:
       
        return AsyncAccessKeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAccessKeysResourceWithStreamingResponse:
      
        return AsyncAccessKeysResourceWithStreamingResponse(self)
    async def validate_create_access_keys_params(self, *, key_name: str, region: str, x_region_id: str) -> None:
        if not isinstance(key_name, str) or not key_name.strip():
            raise ValueError("'key_name' must be a non-empty string.")
        if not isinstance(region, str) or not region.strip():
            raise ValueError("'region' must be a non-empty string.")
        if not isinstance(x_region_id, str) or not x_region_id.strip():
            raise ValueError("'x_region_id' must be a non-empty string.")

    async def validate_delete_access_keys_params(self, *, access_key_id: str, x_region_id: str) -> None:
        if not isinstance(access_key_id, str) or not access_key_id.strip():
            raise ValueError("'access_key_id' must be a non-empty string.")
        if not isinstance(x_region_id, str) or not x_region_id.strip():
            raise ValueError("'x_region_id' must be a non-empty string.")
            
    async def create_access_keys(
        self,
        *,
        key_name: str,
        region: str,
        x_region_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccessKeyCreateResponse:
        """
        Create a new access key

        Args:
          key_name: The name for the access key.

          region: The region associated with the access key.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_create_access_keys_params(
        key_name=key_name,
        region=region,
        x_region_id=x_region_id,
        )

        extra_headers = {"x-region-id": x_region_id, **(extra_headers or {})}
        return await self._post(
            "/kos/v1/access_keys",
            body=await async_maybe_transform(
                {
                    "key_name": key_name,
                    "region": region,
                },
                AccessKeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccessKeyCreateResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccessKeyListResponse:
        """List all access keys for the current user"""
        return await self._get(
            "/kos/v1/access_keys",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccessKeyListResponse,
        )

    async def delete_access_keys(
        self,
        access_key_id: str,
        *,
        x_region_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> dict:
        """
        Delete an access key by its ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not access_key_id:
            raise ValueError(f"Expected a non-empty value for `access_key_id` but received {access_key_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers.update({"x-region-id": x_region_id})
        await self._delete(
            f"/kos/v1/access_keys/{access_key_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )
        return {"access_key_id": access_key_id}

class AccessKeysResourceWithRawResponse:
    def __init__(self, accessKeys: AccessKeysResource) -> None:
        self._accessKeys = accessKeys

        self.create_access_keys = to_raw_response_wrapper(
            accessKeys.create_access_keys,
        )
        self.list = to_raw_response_wrapper(
            accessKeys.list,
        )
        self.delete_access_keys = to_raw_response_wrapper(
            accessKeys.delete_access_keys,
        )


class AsyncAccessKeysResourceWithRawResponse:
    def __init__(self, accessKeys: AsyncAccessKeysResource) -> None:
        self._accessKeys = accessKeys

        self.create_access_keys = async_to_raw_response_wrapper(
            accessKeys.create_access_keys,
        )
        self.list = async_to_raw_response_wrapper(
            accessKeys.list,
        )
        self.delete_access_keys = async_to_raw_response_wrapper(
            accessKeys.delete_access_keys,
        )


class AccessKeysResourceWithStreamingResponse:
    def __init__(self, accessKeys: AccessKeysResource) -> None:
        self._accessKeys = accessKeys

        self.create_access_keys = to_streamed_response_wrapper(
            accessKeys.create_access_keys,
        )
        self.list = to_streamed_response_wrapper(
            accessKeys.list,
        )
        self.delete_access_keys = to_streamed_response_wrapper(
            accessKeys.delete_access_keys,
        )


class AsyncAccessKeysResourceWithStreamingResponse:
    def __init__(self, accessKeys: AsyncAccessKeysResource) -> None:
        self._accessKeys = accessKeys

        self.create_access_keys = async_to_streamed_response_wrapper(
            accessKeys.create_access_keys,
        )
        self.list = async_to_streamed_response_wrapper(
            accessKeys.list,
        )
        self.delete_access_keys = async_to_streamed_response_wrapper(
            accessKeys.delete_access_keys,
        )
