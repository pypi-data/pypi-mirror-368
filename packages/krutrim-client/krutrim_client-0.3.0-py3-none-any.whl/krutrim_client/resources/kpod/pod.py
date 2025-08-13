from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.kpod import pod_create_params, pod_update_params
from ..._base_client import make_request_options

from ...types.kpod.pod_create_response import PodCreateResponse
from ...types.kpod.pod_delete_response import PodDeleteResponse
from ...types.kpod.pod_update_response import PodUpdateResponse

__all__ = ["PodResource", "AsyncPodResource"]


class PodResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PodResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/kpod-python#accessing-raw-response-data-eg-headers
        """
        return PodResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PodResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/kpod-python#with_streaming_response
        """
        return PodResourceWithStreamingResponse(self)
    def validate_create_pod_params(self, *, container_disk_size: str, expose_http_ports: str, expose_tcp_ports: str,
                                         flavor_name: str, pod_name: str, pod_template_id: int, region: str,
                                         sshkey_name: str, volume_disk_size: str, volume_mount_path: str) -> None:
        """
        Validate parameters for creating a pod.
        """
        # Validate the disk size
        if not isinstance(container_disk_size, str) or not container_disk_size.strip():
            raise ValueError("'container_disk_size' must be a non-empty string.")
        
        # Validate the ports
        if not isinstance(expose_http_ports, str) or not expose_http_ports.strip():
            raise ValueError("'expose_http_ports' must be a non-empty string.")
        if not isinstance(expose_tcp_ports, str) or not expose_tcp_ports.strip():
            raise ValueError("'expose_tcp_ports' must be a non-empty string.")
        
        # Validate flavor name
        if not isinstance(flavor_name, str) or not flavor_name.strip():
            raise ValueError("'flavor_name' must be a non-empty string.")
        
        # Validate pod name
        if not isinstance(pod_name, str) or not pod_name.strip():
            raise ValueError("'pod_name' must be a non-empty string.")
        
        # Validate pod template ID
        if not isinstance(pod_template_id, int):
            raise ValueError("'pod_template_id' must be an integer.")
        
        # Validate region
        if not isinstance(region, str) or not region.strip():
            raise ValueError("'region' must be a non-empty string.")
        
        # Validate SSH key name
        if not isinstance(sshkey_name, str) or not sshkey_name.strip():
            raise ValueError("'sshkey_name' must be a non-empty string.")
        
        # Validate volume disk size
        if not isinstance(volume_disk_size, str) or not volume_disk_size.strip():
            raise ValueError("'volume_disk_size' must be a non-empty string.")
        
        # Validate volume mount path
        if not isinstance(volume_mount_path, str) or not volume_mount_path.strip():
            raise ValueError("'volume_mount_path' must be a non-empty string.")

    def validate_delete_pod_params(self, *, kpod_krn: str) -> None:
        """
        Validate parameters for deleting a pod.
        """
        if not isinstance(kpod_krn, str) or not kpod_krn.strip():
            raise ValueError("'kpod_krn' must be a non-empty string.")
        
    def validate_update_pod_params(self, *, kpod_krn: str, action: str) -> None:
        """
        Validate parameters for updating a pod.
        Ensures the pod KRN is a non-empty string and the action is one of "start", "stop", or "restart".
        """
    # Validate the KRN (Krutrim Resource Name) of the pod
        if not isinstance(kpod_krn, str) or not kpod_krn.strip():
            raise ValueError("'kpod_krn' must be a non-empty string.")
    
    # Validate the action to ensure it's one of "start", "stop", or "restart"
        valid_actions = ["start", "stop", "restart"]
        if action not in valid_actions:
            raise ValueError(f"Invalid action: '{action}'. Must be one of {valid_actions}.")
        
    def create(
        self,
        *,
        container_disk_size: str,
        expose_http_ports: str,
        expose_tcp_ports: str,
        flavor_name: str,
        has_encrypt_volume: bool,
        has_jupyter_notebook: bool,
        has_ssh_access: bool,
        pod_name: str,
        pod_template_id: int,
        region: str,
        sshkey_name: str,
        volume_disk_size: str,
        volume_mount_path: str,
        environment_variables: Iterable[object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PodCreateResponse:
        """
        Create a new pod

        Args:
          container_disk_size: The size of the container disk in GB.

          expose_http_ports: Comma-separated list of HTTP ports to expose (e.g., "8888").

          expose_tcp_ports: Comma-separated list of TCP ports to expose (e.g., "22").

          flavor_name: The name of the flavor/instance type for the pod (e.g., GPU type).

          has_encrypt_volume: Indicates if the volume should be encrypted.

          has_jupyter_notebook: Indicates if Jupyter Notebook should be enabled.

          has_ssh_access: Indicates if SSH access should be enabled.

          pod_name: Unique name for the pod.

          pod_template_id: The ID of the pod template to use.

          region: The region where the pod should be deployed.

          sshkey_name: The name of the SSH key to associate with the pod.

          volume_disk_size: The size of the attached volume disk in GB.

          volume_mount_path: The path where the volume should be mounted inside the pod.

          environment_variables: List of environment variables to set in the pod.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_create_pod_params(
            container_disk_size=container_disk_size,
            expose_http_ports=expose_http_ports,
            expose_tcp_ports=expose_tcp_ports,
            flavor_name=flavor_name,
            pod_name=pod_name,
            pod_template_id=pod_template_id,
            region=region,
            sshkey_name=sshkey_name,
            volume_disk_size=volume_disk_size,
            volume_mount_path=volume_mount_path
        )
        return self._post(
            "/v1/kpod/pod",
            body=maybe_transform(
                {
                    "container_disk_size": container_disk_size,
                    "expose_http_ports": expose_http_ports,
                    "expose_tcp_ports": expose_tcp_ports,
                    "flavor_name": flavor_name,
                    "has_encrypt_volume": has_encrypt_volume,
                    "has_jupyter_notebook": has_jupyter_notebook,
                    "has_ssh_access": has_ssh_access,
                    "pod_name": pod_name,
                    "pod_template_id": pod_template_id,
                    "region": region,
                    "sshkey_name": sshkey_name,
                    "volume_disk_size": volume_disk_size,
                    "volume_mount_path": volume_mount_path,
                    "environment_variables": environment_variables,
                },
                pod_create_params.PodCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PodCreateResponse,
        )

    def update(
        self,
        kpod_krn: str,
        *,
        action: Literal["start", "stop", "restart"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PodUpdateResponse:
        """
        Perform an action (e.g., start, stop, restart) on a specific kpod.

        Args:
          kpod_krn: The KRN (Krutrim Resource Name) of the kpod to perform the action on.

          action: The action to perform on the kpod.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_update_pod_params(kpod_krn=kpod_krn, action=action)
        if not kpod_krn:
            raise ValueError(f"Expected a non-empty value for `kpod_krn` but received {kpod_krn!r}")
        
        return self._put(
            f"/v1/kpod/pod/{kpod_krn}",
            body=maybe_transform({"action": action}, pod_update_params.PodUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PodUpdateResponse,
        )

    def delete(
        self,
        kpod_krn: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PodDeleteResponse:
        """
        Delete a specific kpod

        Args:
          kpod_krn: The KRN (Krutrim Resource Name) of the kpod to delete.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        
        if not kpod_krn:
            raise ValueError(f"Expected a non-empty value for `kpod_krn` but received {kpod_krn!r}")
        self.validate_delete_pod_params(kpod_krn=kpod_krn)    
        return self._delete(
            f"/v1/kpod/pod/{kpod_krn}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PodDeleteResponse,
        )


class AsyncPodResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPodResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/kpod-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPodResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPodResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/kpod-python#with_streaming_response
        """
        return AsyncPodResourceWithStreamingResponse(self)
    async def validate_create_pod_params(self, *, container_disk_size: str, expose_http_ports: str, expose_tcp_ports: str,
                                         flavor_name: str, pod_name: str, pod_template_id: int, region: str,
                                         sshkey_name: str, volume_disk_size: str, volume_mount_path: str) -> None:
        """
        Validate parameters for creating a pod.
        """
        if not isinstance(container_disk_size, str) or not container_disk_size.strip():
            raise ValueError("'container_disk_size' must be a non-empty string.")
        if not isinstance(expose_http_ports, str) or not expose_http_ports.strip():
            raise ValueError("'expose_http_ports' must be a non-empty string.")
        if not isinstance(expose_tcp_ports, str) or not expose_tcp_ports.strip():
            raise ValueError("'expose_tcp_ports' must be a non-empty string.")
        if not isinstance(flavor_name, str) or not flavor_name.strip():
            raise ValueError("'flavor_name' must be a non-empty string.")
        if not isinstance(pod_name, str) or not pod_name.strip():
            raise ValueError("'pod_name' must be a non-empty string.")
        if not isinstance(pod_template_id, int):
            raise ValueError("'pod_template_id' must be an integer.")
        if not isinstance(region, str) or not region.strip():
            raise ValueError("'region' must be a non-empty string.")
        if not isinstance(sshkey_name, str) or not sshkey_name.strip():
            raise ValueError("'sshkey_name' must be a non-empty string.")
        if not isinstance(volume_disk_size, str) or not volume_disk_size.strip():
            raise ValueError("'volume_disk_size' must be a non-empty string.")
        if not isinstance(volume_mount_path, str) or not volume_mount_path.strip():
            raise ValueError("'volume_mount_path' must be a non-empty string.")

    async def validate_delete_pod_params(self, *, kpod_krn: str) -> None:
        """
        Validate parameters for deleting a pod.
        """
        if not isinstance(kpod_krn, str) or not kpod_krn.strip():
            raise ValueError("'kpod_krn' must be a non-empty string.")
    async def validate_update_pod_params(self, *, kpod_krn: str, action: str) -> None:
        """
        Validate parameters for updating a pod.
        Ensures the pod KRN is a non-empty string and the action is one of "start", "stop", or "restart".
        """
    # Validate the KRN (Krutrim Resource Name) of the pod
        if not isinstance(kpod_krn, str) or not kpod_krn.strip():
            raise ValueError("'kpod_krn' must be a non-empty string.")
    
    # Validate the action to ensure it's one of "start", "stop", or "restart"
        valid_actions = ["start", "stop", "restart"]
        if action not in valid_actions:
            raise ValueError(f"Invalid action: '{action}'. Must be one of {valid_actions}.")
        
    async def create(
        self,
        *,
        container_disk_size: str,
        expose_http_ports: str,
        expose_tcp_ports: str,
        flavor_name: str,
        has_encrypt_volume: bool,
        has_jupyter_notebook: bool,
        has_ssh_access: bool,
        pod_name: str,
        pod_template_id: int,
        region: str,
        sshkey_name: str,
        volume_disk_size: str,
        volume_mount_path: str,
        environment_variables: Iterable[object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PodCreateResponse:
        """
        Create a new pod

        Args:
          container_disk_size: The size of the container disk in GB.

          expose_http_ports: Comma-separated list of HTTP ports to expose (e.g., "8888").

          expose_tcp_ports: Comma-separated list of TCP ports to expose (e.g., "22").

          flavor_name: The name of the flavor/instance type for the pod (e.g., GPU type).

          has_encrypt_volume: Indicates if the volume should be encrypted.

          has_jupyter_notebook: Indicates if Jupyter Notebook should be enabled.

          has_ssh_access: Indicates if SSH access should be enabled.

          pod_name: Unique name for the pod.

          pod_template_id: The ID of the pod template to use.

          region: The region where the pod should be deployed.

          sshkey_name: The name of the SSH key to associate with the pod.

          volume_disk_size: The size of the attached volume disk in GB.

          volume_mount_path: The path where the volume should be mounted inside the pod.

          environment_variables: List of environment variables to set in the pod.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_create_pod_params(
            container_disk_size=container_disk_size,
            expose_http_ports=expose_http_ports,
            expose_tcp_ports=expose_tcp_ports,
            flavor_name=flavor_name,
            pod_name=pod_name,
            pod_template_id=pod_template_id,
            region=region,
            sshkey_name=sshkey_name,
            volume_disk_size=volume_disk_size,
            volume_mount_path=volume_mount_path
        )
        return await self._post(
            "/v1/kpod/pod",
            body=await async_maybe_transform(
                {
                    "container_disk_size": container_disk_size,
                    "expose_http_ports": expose_http_ports,
                    "expose_tcp_ports": expose_tcp_ports,
                    "flavor_name": flavor_name,
                    "has_encrypt_volume": has_encrypt_volume,
                    "has_jupyter_notebook": has_jupyter_notebook,
                    "has_ssh_access": has_ssh_access,
                    "pod_name": pod_name,
                    "pod_template_id": pod_template_id,
                    "region": region,
                    "sshkey_name": sshkey_name,
                    "volume_disk_size": volume_disk_size,
                    "volume_mount_path": volume_mount_path,
                    "environment_variables": environment_variables,
                },
                pod_create_params.PodCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PodCreateResponse,
        )

    async def update(
        self,
        kpod_krn: str,
        *,
        action: Literal["start", "stop", "restart"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PodUpdateResponse:
        """
        Perform an action (e.g., start, stop, restart) on a specific kpod.

        Args:
          kpod_krn: The KRN (Krutrim Resource Name) of the kpod to perform the action on.

          action: The action to perform on the kpod.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_update_pod_params(kpod_krn=kpod_krn, action=action)
        if not kpod_krn:
            raise ValueError(f"Expected a non-empty value for `kpod_krn` but received {kpod_krn!r}")
        return await self._put(
            f"/v1/kpod/pod/{kpod_krn}",
            body=await async_maybe_transform({"action": action}, pod_update_params.PodUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PodUpdateResponse,
        )


    async def delete(
        self,
        kpod_krn: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PodDeleteResponse:
        """
        Delete a specific kpod

        Args:
          kpod_krn: The KRN (Krutrim Resource Name) of the kpod to delete.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_delete_pod_params(kpod_krn=kpod_krn) 
        # if not kpod_krn:
        #     raise ValueError(f"Expected a non-empty value for `kpod_krn` but received {kpod_krn!r}")
           
        return await self._delete(
            f"/v1/kpod/pod/{kpod_krn}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PodDeleteResponse,
        )


class PodResourceWithRawResponse:
    def __init__(self, pod: PodResource) -> None:
        self._pod = pod

        self.create = to_raw_response_wrapper(
            pod.create,
        )
        self.update = to_raw_response_wrapper(
            pod.update,
        )
        self.delete = to_raw_response_wrapper(
            pod.delete,
        )


class AsyncPodResourceWithRawResponse:
    def __init__(self, pod: AsyncPodResource) -> None:
        self._pod = pod

        self.create = async_to_raw_response_wrapper(
            pod.create,
        )
        self.update = async_to_raw_response_wrapper(
            pod.update,
        )
        self.delete = async_to_raw_response_wrapper(
            pod.delete,
        )


class PodResourceWithStreamingResponse:
    def __init__(self, pod: PodResource) -> None:
        self._pod = pod

        self.create = to_streamed_response_wrapper(
            pod.create,
        )
        self.update = to_streamed_response_wrapper(
            pod.update,
        )
        self.delete = to_streamed_response_wrapper(
            pod.delete,
        )


class AsyncPodResourceWithStreamingResponse:
    def __init__(self, pod: AsyncPodResource) -> None:
        self._pod = pod

        self.create = async_to_streamed_response_wrapper(
            pod.create,
        )
        self.update = async_to_streamed_response_wrapper(
            pod.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            pod.delete,
        )
