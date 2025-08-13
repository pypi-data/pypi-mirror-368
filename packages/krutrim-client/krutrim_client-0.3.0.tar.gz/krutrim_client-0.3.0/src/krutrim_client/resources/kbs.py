from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

from .._resource import SyncAPIResource, AsyncAPIResource
from .._base_client import make_request_options
import httpx
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven, Base64FileInput
# from ..types.kbs import 

from ..types.kbs import (
    volume_create_params,
    QosParam,
    SourceParam,
    VolumeDetail
)


from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)


__all__ = ["KbsResource", "AsyncKbsResource"]

class KbsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> KbsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.
        """
        return KbsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> KbsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        """
        return KbsResourceWithStreamingResponse(self)
    


    def validate_delete_volume_parameters(
    self,
    id: str,
    k_tenant_id: str,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        # Validate 'id'
        if not isinstance(id, str) or not id.strip():
            raise ValueError("'id' must be a non-empty string.")

        # Validate 'k_tenant_id'
        if not isinstance(k_tenant_id, str) or not k_tenant_id.strip():
            raise ValueError("'k_tenant_id' must be a non-empty string.")

        # Validate optional dictionary parameters
        for name, param in {
            "extra_headers": extra_headers,
            "extra_query": extra_query,
            "extra_body": extra_body,
        }.items():
            if param is not None and not isinstance(param, dict):
                raise ValueError(f"'{name}' must be a dictionary if provided.")

        # Validate timeout
        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")



    def validate_create_volume_parameters(
    self,
    availability_zone,
    multiattach,
    name,
    size,
    x_region,
    volumetype,
    k_tenant_id,
    timeout=None
    
    ):
        # Required string parameters
        for param_name, param_value in {
            "availability_zone": availability_zone,
            "name": name,
            "volumetype": volumetype,
            "k_tenant_id": k_tenant_id,
        }.items():
            if not isinstance(param_value, str) or not param_value:
                raise ValueError(f"'{param_name}' must be a non-empty string.")

        # Required: multiattach
        if not isinstance(multiattach, bool):
            raise ValueError("'multiattach' must be a boolean.")

        # Required: size
        if not isinstance(size, int) or size <= 0:
            raise ValueError("'size' must be a positive integer.")


        # Optional: timeout
        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")




    def delete_volume (
        self,
        id: str,
        *,
        k_tenant_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a KBS Volume

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_delete_volume_parameters(
            id = id,
            k_tenant_id = k_tenant_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            x_region = x_region
        )
        extra_headers = {
            "K-Tenant-ID": k_tenant_id,
            "x-region": x_region,
            **(extra_headers or {})
        }
        return self._delete(
            f"/kbs/v1/volumes/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def create_volume(
        self,
        *,
        availability_zone: str,
        multiattach: bool,
        name: str,
        size: int,
        volumetype: str,
        k_tenant_id: str,
        x_region: str,
        description: Optional[str] | None | NotGiven = NOT_GIVEN,
        metadata: dict| None | NotGiven = NOT_GIVEN,
        qos: QosParam | None | NotGiven = NOT_GIVEN,
        source: SourceParam | None | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VolumeDetail:
        """
        Create a new KBS Volume

        Args:
          availability_zone: Availability zone for the volume.

          multiattach: Whether the volume can be attached to multiple instances.

          name: Name of the volume.

          size: Size of the volume in GB.

          volumetype: Type of the volume.

          description: Description of the volume.

          metadata: Metadata key-value pairs for the volume.

          qos: Quality of Service (QoS) settings for the volume.

          source: Source from which the volume is created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_create_volume_parameters(
            availability_zone = availability_zone,
            multiattach = multiattach,
            name = name,
            size = size,
            volumetype = volumetype,
            k_tenant_id = k_tenant_id,
            timeout=timeout,
            x_region = x_region
        )

        extra_headers = {"K-Tenant-ID": k_tenant_id, **(extra_headers or {})}
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/kbs/v1/volumes",
            body=maybe_transform(
                {
                    "availability_zone": availability_zone,
                    "multiattach": multiattach,
                    "name": name,
                    "size": size,
                    "volumetype": volumetype,
                    "description": description,
                    "metadata": metadata,
                    "qos": qos,
                    "source": source,
                },
                volume_create_params.VolumeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VolumeDetail,
        )
    # GET VOLUME
    def retrieve_volume(
        self,
        volume_id: str,
        *,
        k_tenant_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VolumeDetail:
        """
        Get details of a specific KBS Volume

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not volume_id:
            raise ValueError(f"Expected a non-empty value for `volume_id` but received {volume_id!r}")
        extra_headers = {"K-Tenant-ID": k_tenant_id, **(extra_headers or {})}
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._get(
            f"/kbs/v1/volumes/{volume_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VolumeDetail,
        )





class AsyncKbsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncKbsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.
        """
        return AsyncKbsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncKbsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.
        """
        return AsyncKbsResourceWithStreamingResponse(self)
    


    async def validate_delete_volume_parameters(
    self,
    id: str,
    k_tenant_id: str,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        # Validate 'id'
        if not isinstance(id, str) or not id.strip():
            raise ValueError("'id' must be a non-empty string.")

        # Validate 'k_tenant_id'
        if not isinstance(k_tenant_id, str) or not k_tenant_id.strip():
            raise ValueError("'k_tenant_id' must be a non-empty string.")

        # Validate optional dictionary parameters
        for name, param in {
            "extra_headers": extra_headers,
            "extra_query": extra_query,
            "extra_body": extra_body,
        }.items():
            if param is not None and not isinstance(param, dict):
                raise ValueError(f"'{name}' must be a dictionary if provided.")

        # Validate timeout
        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")


    async def validate_create_volume_parameters(
    self,
    availability_zone,
    multiattach,
    name,
    size,
    x_region,
    volumetype,
    k_tenant_id,
    timeout=None
    
    ):
        # Required string parameters
        for param_name, param_value in {
            "availability_zone": availability_zone,
            "name": name,
            "volumetype": volumetype,
            "k_tenant_id": k_tenant_id,
        }.items():
            if not isinstance(param_value, str) or not param_value:
                raise ValueError(f"'{param_name}' must be a non-empty string.")

        # Required: multiattach
        if not isinstance(multiattach, bool):
            raise ValueError("'multiattach' must be a boolean.")

        # Required: size
        if not isinstance(size, int) or size <= 0:
            raise ValueError("'size' must be a positive integer.")


        # Optional: timeout
        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")

    async def delete_volume(
        self,
        id: str,
        *,
        k_tenant_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a KBS Volume

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_delete_volume_parameters(
            id = id,
            k_tenant_id = k_tenant_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            x_region = x_region
        )
        extra_headers = {
            "K-Tenant-ID": k_tenant_id,
            "x-region": x_region,
            **(extra_headers or {})
        }

        return await self._delete(
            f"/kbs/v1/volumes/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def create_volume(
        self,
        *,
        availability_zone: str,
        multiattach: bool,
        name: str,
        size: int,
        volumetype: str,
        k_tenant_id: str,
        x_region: str,
        description: Optional[str] | None | NotGiven = NOT_GIVEN,
        metadata: dict| None | NotGiven = NOT_GIVEN,
        qos: QosParam | None | NotGiven = NOT_GIVEN,
        source: SourceParam | None | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VolumeDetail:
        """
        Create a new KBS Volume

        Args:
          availability_zone: Availability zone for the volume.

          multiattach: Whether the volume can be attached to multiple instances.

          name: Name of the volume.

          size: Size of the volume in GB.

          volumetype: Type of the volume.

          description: Description of the volume.

          metadata: Metadata key-value pairs for the volume.

          qos: Quality of Service (QoS) settings for the volume.

          source: Source from which the volume is created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_create_volume_parameters(
            availability_zone = availability_zone,
            multiattach = multiattach,
            name = name,
            size = size,
            volumetype = volumetype,
            k_tenant_id = k_tenant_id,
            timeout=timeout,
            x_region = x_region
        )


        extra_headers = {"K-Tenant-ID": k_tenant_id, **(extra_headers or {})}
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/kbs/v1/volumes",
            body=await async_maybe_transform(
                {
                    "availability_zone": availability_zone,
                    "multiattach": multiattach,
                    "name": name,
                    "size": size,
                    "volumetype": volumetype,
                    "description": description,
                    "metadata": metadata,
                    "qos": qos,
                    "source": source,
                },
                volume_create_params.VolumeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VolumeDetail,
        )


    async def retrieve_volume(
        self,
        volume_id: str,
        *,
        k_tenant_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VolumeDetail:
        """
        Get details of a specific KBS Volume

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not volume_id:
            raise ValueError(f"Expected a non-empty value for `volume_id` but received {volume_id!r}")
        extra_headers = {"K-Tenant-ID": k_tenant_id, **(extra_headers or {})}
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._get(
            f"/kbs/v1/volumes/{volume_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VolumeDetail,
        )




class KbsResourceWithRawResponse:
    def __init__(self, kbs: KbsResource) -> None:
        self._kbs = kbs

        self.delete_security_group = to_raw_response_wrapper(
            kbs.create_volume,
        )
        
        self.create_security_group = to_raw_response_wrapper(
            kbs.delete_volume,
        )

        self.create_rule = to_raw_response_wrapper(
            kbs.retrieve_volume,
        )




class AsyncKbsResourceWithRawResponse:
    def __init__(self, kbs: AsyncKbsResource) -> None:
        self._kbs = kbs

        self.delete_security_group = async_to_raw_response_wrapper(
            kbs.create_volume,
        )

        self.create_security_group = async_to_raw_response_wrapper(
            kbs.delete_volume,
        )

        self.create_rule = async_to_raw_response_wrapper(
            kbs.retrieve_volume,
        )
        


class KbsResourceWithStreamingResponse:
    def __init__(self, kbs: KbsResource) -> None:
        self._kbs = kbs

        self.delete_security_group = to_streamed_response_wrapper(
            kbs.create_volume,
        )

        self.create_security_group = to_streamed_response_wrapper(
            kbs.delete_volume,
        )

        self.create_rule = to_streamed_response_wrapper(
            kbs.retrieve_volume,
        )


class AsyncKbsResourceWithStreamingResponse:
    def __init__(self, kbs: AsyncKbsResource) -> None:
        self._kbs = kbs

        self.delete_security_group = async_to_streamed_response_wrapper(
            kbs.create_volume,
        )

        self.create_security_group = async_to_streamed_response_wrapper(
            kbs.delete_volume,
        )
        
        self.create_rule = async_to_streamed_response_wrapper(
            kbs.retrieve_volume,
        )


        

    
