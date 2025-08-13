from __future__ import annotations

from typing import Dict

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
from ...types.kos.buckets.bucket_create_params import BucketCreateParams
from ...types.kos.buckets.bucket_create_response import BucketCreateResponse
from ...types.kos.buckets.bucket_list_response import BucketListResponse



__all__ = ["BucketsResource", "AsyncBucketsResource"]


class BucketsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BucketsResourceWithRawResponse:
       
        return BucketsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BucketsResourceWithStreamingResponse:
        
        return BucketsResourceWithStreamingResponse(self)
    def validate_create_bucket_params(self, *, name: str, region: str, x_region_id: str) -> None:
    # Ensure the bucket name is a non-empty string
        if not isinstance(name, str) or not name.strip():
            raise ValueError("'name' must be a non-empty string.")
    
    # Ensure the region is a non-empty string
        if not isinstance(region, str) or not region.strip():
            raise ValueError("'region' must be a non-empty string.")
    
    # Ensure the region ID is a non-empty string
        if not isinstance(x_region_id, str) or not x_region_id.strip():
            raise ValueError("'x_region_id' must be a non-empty string.")

    def validate_delete_bucket_params(self, *, bucket_krn: str, x_region_id: str) -> None:
    # Ensure the bucket KRN is a non-empty string
        if not isinstance(bucket_krn, str) or not bucket_krn.strip():
            raise ValueError("'bucket_krn' must be a non-empty string.")
    
    # Ensure the region ID is a non-empty string
        if not isinstance(x_region_id, str) or not x_region_id.strip():
            raise ValueError("'x_region_id' must be a non-empty string.")
        

    def create_bucket(
        self,
        *,
        name: str,
        region: str,
        x_region_id: str,
        anonymous_access: bool | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        tags: Dict[str, str] | NotGiven = NOT_GIVEN,
        versioning: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BucketCreateResponse:
        """
        Create a new bucket

        Args:
          name: The name of the bucket.

          region: The region where the bucket will be created.

          anonymous_access: Whether anonymous access is allowed for the bucket.

          description: A description for the bucket.

          tags: Key-value tags associated with the bucket.

          versioning: Whether versioning is enabled for the bucket.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_create_bucket_params(name=name, region=region, x_region_id=x_region_id)
        extra_headers = {"x-region-id": x_region_id, **(extra_headers or {})}
        return self._post(
            "/kos/v1/buckets",
            body=maybe_transform(
                {
                    "name": name,
                    "region": region,
                    "anonymous_access": anonymous_access,
                    "description": description,
                    "tags": tags,
                    "versioning": versioning,
                },
                BucketCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BucketCreateResponse,
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
    ) -> BucketListResponse:
        """List all buckets for the current user"""
        return self._get(
            "/kos/v1/buckets",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BucketListResponse,
        )

    def delete_bucket(
        self,
        bucket_krn: str,
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
        Delete a bucket by its KRN (KOS Resource Name)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not bucket_krn:
            raise VxalueError(f"Expected a non-empty value for `bucket_krn` but received {bucket_krn!r}")
        self.validate_delete_bucket_params(bucket_krn=bucket_krn, x_region_id=x_region_id)    
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers.update({"x-region-id": x_region_id})
        self._delete(
            f"/kos/v1/buckets/{bucket_krn}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )
        return {"bucket_krn": bucket_krn}


class AsyncBucketsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBucketsResourceWithRawResponse:
        
        return AsyncBucketsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBucketsResourceWithStreamingResponse:
        
        return AsyncBucketsResourceWithStreamingResponse(self)
    async def validate_create_bucket_params(self, *, name: str, region: str, x_region_id: str) -> None:
        """
        Validate parameters for creating a bucket.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("'name' must be a non-empty string.")
        
        if not isinstance(region, str) or not region.strip():
            raise ValueError("'region' must be a non-empty string.")
        
        if not isinstance(x_region_id, str) or not x_region_id.strip():
            raise ValueError("'x_region_id' must be a non-empty string.")

    async def validate_delete_bucket_params(self, *, bucket_krn: str, x_region_id: str) -> None:
        """
        Validate parameters for deleting a bucket.
        """
        if not isinstance(bucket_krn, str) or not bucket_krn.strip():
            raise ValueError("'bucket_krn' must be a non-empty string.")
        
        if not isinstance(x_region_id, str) or not x_region_id.strip():
            raise ValueError("'x_region_id' must be a non-empty string.")


    async def create_bucket(
        self,
        *,
        name: str,
        region: str,
        x_region_id: str,
        anonymous_access: bool | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        tags: Dict[str, str] | NotGiven = NOT_GIVEN,
        versioning: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BucketCreateResponse:
        """
        Create a new bucket

        Args:
          name: The name of the bucket.

          region: The region where the bucket will be created.

          anonymous_access: Whether anonymous access is allowed for the bucket.

          description: A description for the bucket.

          tags: Key-value tags associated with the bucket.

          versioning: Whether versioning is enabled for the bucket.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_create_bucket_params(name=name, region=region, x_region_id=x_region_id)
        extra_headers = {"x-region-id": x_region_id, **(extra_headers or {})}
        return await self._post(
            "/kos/v1/buckets",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "region": region,
                    "anonymous_access": anonymous_access,
                    "description": description,
                    "tags": tags,
                    "versioning": versioning,
                },
                BucketCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BucketCreateResponse,
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
    ) -> BucketListResponse:
        """List all buckets for the current user"""
        return await self._get(
            "/kos/v1/buckets",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BucketListResponse,
        )

    async def delete_bucket(
        self,
        bucket_krn: str,
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
        Delete a bucket by its KRN (KOS Resource Name)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not bucket_krn:
            raise ValueError(f"Expected a non-empty value for `bucket_krn` but received {bucket_krn!r}")
        await self.validate_delete_bucket_params(bucket_krn=bucket_krn, x_region_id=x_region_id)
    
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers.update({"x-region-id": x_region_id})
        await self._delete(
            f"/kos/v1/buckets/{bucket_krn}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )
        return {"bucket_krn": bucket_krn}



class BucketsResourceWithRawResponse:
    def __init__(self, buckets: BucketsResource) -> None:
        self._buckets = buckets

        self.create_bucket= to_raw_response_wrapper(
            buckets.create_bucket,
        )
        self.list = to_raw_response_wrapper(
            buckets.list,
        )
        self.delete_bucket= to_raw_response_wrapper(
            buckets.delete_bucket,
        )


class AsyncBucketsResourceWithRawResponse:
    def __init__(self, buckets: AsyncBucketsResource) -> None:
        self._buckets = buckets

        self.create_bucket = async_to_raw_response_wrapper(
            buckets.create_bucket,
        )
        self.list = async_to_raw_response_wrapper(
            buckets.list,
        )
        self.delete_bucket= async_to_raw_response_wrapper(
            buckets.delete_bucket,
        )


class BucketsResourceWithStreamingResponse:
    def __init__(self, buckets: BucketsResource) -> None:
        self._buckets = buckets

        self.create_bucket = to_streamed_response_wrapper(
            buckets.create_bucket,
        )
        self.list = to_streamed_response_wrapper(
            buckets.list,
        )
        self.delete_bucket = to_streamed_response_wrapper(
            buckets.delete_bucket,
        )


class AsyncBucketsResourceWithStreamingResponse:
    def __init__(self, buckets: AsyncBucketsResource) -> None:
        self._buckets = buckets

        self.create_bucket = async_to_streamed_response_wrapper(
            buckets.create_bucket,
        )
        self.list = async_to_streamed_response_wrapper(
            buckets.list,
        )
        self.delete_bucket= async_to_streamed_response_wrapper(
            buckets.delete_bucket,
        )



