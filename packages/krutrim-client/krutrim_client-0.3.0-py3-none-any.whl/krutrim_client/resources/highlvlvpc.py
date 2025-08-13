
from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

import httpx

from typing import Dict

from ..types.highlvlvpc import (
    highlvlvpc_create_vpc_params,
    highlvlvpc_delete_vpc_params,
    highlvlvpc_create_port_params,
    highlvlvpc_search_vpcs_params,
    highlvlvpc_retrieve_vpc_params,
    highlvlvpc_search_ports_params,
    highlvlvpc_create_subnet_params,
    highlvlvpc_create_instance_params,
    highlvlvpc_delete_instance_params,
    highlvlvpc_search_networks_params,
    highlvlvpc_search_instances_params,
    highlvlvpc_retrieve_instance_params,
    highlvlvpc_list_instance_info_params,
    highlvlvpc_get_vpc_task_status_params,
    highlvlvpc_create_image_params,
    highlvlvpc_list_image_params,
    highlvlvpc_delete_image_params,
    QosParam,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven, Base64FileInput
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
# from ..types.image_list import ImageList
from ..types.highlvlvpc.vpc_detail import VpcDetail
from ..types.highlvlvpc.port_detail import PortDetail
from ..types.highlvlvpc.instance_info import InstanceInfo
from ..types.highlvlvpc.success_response import SuccessResponse
from ..types.highlvlvpc.instance_info_list import InstanceInfoList
from ..types.highlvlvpc.highlvlvpc_list_vpcs_response import HighlvlvpcListVpcsResponse
from ..types.highlvlvpc.highlvlvpc_search_vpcs_response import HighlvlvpcSearchVpcsResponse
from ..types.highlvlvpc.highlvlvpc_search_ports_response import HighlvlvpcSearchPortsResponse
from ..types.highlvlvpc.highlvlvpc_search_networks_response import HighlvlvpcSearchNetworksResponse
from ..types.highlvlvpc.highlvlvpc_create_image_response import HighlvlvpcCreateImageResponse
from ..types.highlvlvpc.highlvlvpc_list_image_response import HighlvlvpcListImageResponse



__all__ = ["HighlvlvpcResource", "AsyncHighlvlvpcResource"]


class HighlvlvpcResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> HighlvlvpcResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.
        """
        return HighlvlvpcResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HighlvlvpcResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        """
        return HighlvlvpcResourceWithStreamingResponse(self)


    def validate_create_subnet_parameters(
    self,
    subnet_data,
    vpc_id,
    router_krn,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        if not isinstance(subnet_data, dict):
            raise ValueError("'subnet_data' must be a dictionary.")

        required_fields = ["cidr", "ip_version", "name"]
        for field in required_fields:
            if field not in subnet_data:
                raise ValueError(f"'{field}' is required in subnet_data.")
        
        if not isinstance(subnet_data["cidr"], str):
            raise ValueError("'cidr' must be a string.")
        
        if subnet_data["ip_version"] not in (4, 6):
            raise ValueError("'ip_version' must be either 4 or 6.")
        
        if not isinstance(subnet_data["name"], str):
            raise ValueError("'name' must be a string.")

        if "description" in subnet_data and not isinstance(subnet_data["description"], str):
            raise ValueError("'description' must be a string if provided.")

        if "gateway_ip" in subnet_data and not isinstance(subnet_data["gateway_ip"], str):
            raise ValueError("'gateway_ip' must be a string if provided.")

        if not isinstance(vpc_id, str):
            raise ValueError("'vpc_id' must be a string.")
        
        if not isinstance(router_krn, str):
            raise ValueError("'router_krn' must be a string.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")


    

    def validate_create_instance_parameters(
    self,
    image_krn,
    instanceName,
    instanceType,
    network_id,
    security_groups,
    sshkey_name,
    subnet_id,
    vm_volume_disk_size,
    vpc_id,
    x_region,
    floating_ip=None,
    user_data=None,
    volume_name=None,
    volume_size=None,
    volumetype=None,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None,
    qos=None,
    tags=None
    ):
        for name, value in {
            "image_krn": image_krn,
            "instanceName": instanceName,
            "instanceType": instanceType,
            "network_id": network_id,
            "sshkey_name": sshkey_name,
            "subnet_id": subnet_id,
            "vm_volume_disk_size": vm_volume_disk_size,
            "vpc_id": vpc_id,
            "volumetype": volumetype,
        }.items():
            if not isinstance(value, str) or not value:
                raise ValueError(f"'{name}' must be a non-empty string.")

        # Optional: floating_ip
        if floating_ip is not None and not isinstance(floating_ip, bool):
            raise ValueError("'floating_ip' must be a boolean if provided.")

        # Optional: user_data
        if user_data is not None and not isinstance(user_data, (str, dict)):
            raise ValueError("'user_data' must be a string or Base64FileInput (dict) if provided.")

        # Optional: volume_name
        if volume_name is not None and not isinstance(volume_name, str):
            raise ValueError("'volume_name' must be a string if provided.")

        # Optional: volume_size
        if volume_size is not None and not isinstance(volume_size, int):
            raise ValueError("'volume_size' must be an integer if provided.")

        # Optional: extra dicts
        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")
        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")
        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        # Optional: timeout
        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        # qos
        if not isinstance(qos, dict):
            raise ValueError("'qos' must be a dictionary.")

        # tags
        if not isinstance(tags, list):
            raise ValueError("'tags' must be a list.")

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



    def validate_create_vpc_parameters(
    self,
    network: dict,
    security_group: dict,
    security_group_rule: dict,
    subnet: dict,
    vpc: dict,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
        ):
        # --- network ---
        if not isinstance(network, dict):
            raise ValueError("'network' must be a dictionary.")
        if "name" not in network or not isinstance(network["name"], str):
            raise ValueError("'network.name' must be a non-empty string.")
        if "admin_state_up" not in network or not isinstance(network["admin_state_up"], bool):
            raise ValueError("'network.admin_state_up' must be a boolean.")

        # --- security_group ---
        if not isinstance(security_group, dict):
            raise ValueError("'security_group' must be a dictionary.")
        if "name" not in security_group or not isinstance(security_group["name"], str):
            raise ValueError("'security_group.name' must be a string.")
        if "description" not in security_group or not isinstance(security_group["description"], str):
            raise ValueError("'security_group.description' must be a string.")

        # --- security_group_rule ---
        if not isinstance(security_group_rule, dict):
            raise ValueError("'security_group_rule' must be a dictionary.")
        if security_group_rule.get("direction") not in ("ingress", "egress"):
            raise ValueError("'security_group_rule.direction' must be 'ingress' or 'egress'.")
        if security_group_rule.get("ethertypes") not in ("IPv4", "IPv6"):
            raise ValueError("'security_group_rule.ethertypes' must be 'IPv4' or 'IPv6'.")
        if not isinstance(security_group_rule.get("protocol"), str):
            raise ValueError("'security_group_rule.protocol' must be a string.")
        if not isinstance(security_group_rule.get("portMinRange"), int):
            raise ValueError("'security_group_rule.portMinRange' must be an integer.")
        if not isinstance(security_group_rule.get("portMaxRange"), int):
            raise ValueError("'security_group_rule.portMaxRange' must be an integer.")
        if not isinstance(security_group_rule.get("remoteIPPrefix"), str):
            raise ValueError("'security_group_rule.remoteIPPrefix' must be a string.")

        # --- subnet ---
        if not isinstance(subnet, dict):
            raise ValueError("'subnet' must be a dictionary.")
        for key in ("cidr", "gateway_ip", "name", "description"):
            if key not in subnet or not isinstance(subnet[key], str):
                raise ValueError(f"'subnet.{key}' must be a string.")
        if subnet.get("ip_version") not in (4, 6):
            raise ValueError("'subnet.ip_version' must be 4 or 6.")
        if not isinstance(subnet.get("ingress"), bool):
            raise ValueError("'subnet.ingress' must be a boolean.")
        if not isinstance(subnet.get("egress"), bool):
            raise ValueError("'subnet.egress' must be a boolean.")

        # --- vpc ---
        if not isinstance(vpc, dict):
            raise ValueError("'vpc' must be a dictionary.")
        if "name" not in vpc or not isinstance(vpc["name"], str):
            raise ValueError("'vpc.name' must be a string.")
        if "description" not in vpc or not isinstance(vpc["description"], str):
            raise ValueError("'vpc.description' must be a string.")
        if "enabled" not in vpc or not isinstance(vpc["enabled"], bool):
            raise ValueError("'vpc.enabled' must be a boolean.")

        # --- optional extras ---
        for name, param in {
            "extra_headers": extra_headers,
            "extra_query": extra_query,
            "extra_body": extra_body,
        }.items():
            if param is not None and not isinstance(param, dict):
                raise ValueError(f"'{name}' must be a dictionary if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")

    def validate_delete_instance_parameters(
    self,
    instanceKrn: str,
    deleteVolume: bool,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        # Validate instanceKrn
        if not isinstance(instanceKrn, str) or not instanceKrn.strip():
            raise ValueError("'instanceKrn' must be a non-empty string.")

        # Validate deleteVolume
        if not isinstance(deleteVolume, bool):
            raise ValueError("'deleteVolume' must be a boolean.")

        # Validate extra headers/query/body if provided
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

    

  
    def validate_delete_vpc_parameters(
    self,
    vpc_id: str,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        # Validate 'vpc_id'
        if not isinstance(vpc_id, str) or not vpc_id.strip():
            raise ValueError("'vpc_id' must be a non-empty string.")

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


    def validate_list_instance_info_parameters(
    self,
    vpc_id: str,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None,
    page=None,
    page_size=None
    ):
        # Validate 'vpc_id'
        if not isinstance(vpc_id, str) or not vpc_id.strip():
            raise ValueError("'vpc_id' must be a non-empty string.")

        # Validate 'page' if provided
        if page is not None:
            if not isinstance(page, int) or page < 1:
                raise ValueError("'page' must be a positive integer if provided.")

        # Validate 'page_size' if provided
        if page_size is not None:
            if not isinstance(page_size, int) or page_size < 1:
                raise ValueError("'page_size' must be a positive integer if provided.")

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


    def validate_retrieve_instance_parameters(
    self,
    krn: str,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        if not isinstance(krn, str) or not krn.strip():
            raise ValueError("'krn' must be a non-empty string.")

        for name, param in {
            "extra_headers": extra_headers,
            "extra_query": extra_query,
            "extra_body": extra_body,
        }.items():
            if param is not None and not isinstance(param, dict):
                raise ValueError(f"'{name}' must be a dictionary if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")
        
        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")


    def validate_get_vpc_task_status_params(
    self,
    task_id: str,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("'task_id' must be a non-empty string.")

        for name, param in {
            "extra_headers": extra_headers,
            "extra_query": extra_query,
            "extra_body": extra_body,
        }.items():
            if param is not None and not isinstance(param, dict):
                raise ValueError(f"'{name}' must be a dict if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")
        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")


    def validate_search_instances_params(
    self,
    vpc_id: str,
    x_region,
    x_user_email = NOT_GIVEN,
    limit = NOT_GIVEN,
    page = NOT_GIVEN,
    ip_fixed = NOT_GIVEN,
    ip_floating = NOT_GIVEN,
    krn = NOT_GIVEN,
    name = NOT_GIVEN
    ):
        if not isinstance(vpc_id, str) or not vpc_id.strip():
            raise ValueError("vpc_id must be a non-empty string.")
        
        if x_user_email is not NOT_GIVEN and x_user_email is not None:
            if not isinstance(x_user_email, str) or "@" not in x_user_email:
                raise ValueError("x_user_email must be a valid email string.")
        
        if limit is not NOT_GIVEN and limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                raise ValueError("limit must be a positive integer.")

        if page is not NOT_GIVEN and page is not None:
            if not isinstance(page, int) or page <= 0:
                raise ValueError("page must be a positive integer.")

        def _validate_ip(ip):
            if ip is not NOT_GIVEN and ip is not None:
                if not isinstance(ip, str) or not ip:
                    raise ValueError("IP address must be a non-empty string.")

        _validate_ip(ip_fixed)
        _validate_ip(ip_floating)

        if krn is not NOT_GIVEN and krn is not None:
            if not isinstance(krn, str) or not krn.strip():
                raise ValueError("krn must be a non-empty string if provided.")
        
        if name is not NOT_GIVEN and name is not None:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("name must be a non-empty string if provided.")
        
        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")



    def validate_search_networks_parameters(
    self,
    vpc_id,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        # Required: vpc_id must be a non-empty string
        if not isinstance(vpc_id, str) or not vpc_id:
            raise ValueError("'vpc_id' must be a non-empty string.")

        # Optional: extra_headers must be a dictionary if provided
        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")

        # Optional: extra_query must be a dictionary if provided
        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")

        # Optional: extra_body must be a dictionary if provided
        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        # Optional: timeout must be float/int/httpx.Timeout if provided
        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (float, int, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")
        
        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")
    
    def validate_create_port_parameters(
    self,
    *,
    floating_ip,
    name,
    network_id,
    subnet_id,
    vpc_id,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        # Required: floating_ip must be a boolean
        if not isinstance(floating_ip, bool):
            raise ValueError("'floating_ip' must be a boolean.")

        # Required string parameters
        for param_name, param_value in {
            "name": name,
            "network_id": network_id,
            "subnet_id": subnet_id,
            "vpc_id": vpc_id,
        }.items():
            if not isinstance(param_value, str) or not param_value:
                raise ValueError(f"'{param_name}' must be a non-empty string.")

        # Optional: extra_headers must be a dictionary if provided
        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")

        # Optional: extra_query must be a dictionary if provided
        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")

        # Optional: extra_body must be a dictionary if provided
        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        # Optional: timeout must be float/int/httpx.Timeout if provided
        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (float, int, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")

    def validate_create_image_parameters(
        self,
        name: str,
        instance_krn: str,
        x_region: str,
        timeout: float | NotGiven = NOT_GIVEN
    ):
        # Validate 'name' is a non-empty string
        if not isinstance(name, str) or not name.strip():
            raise ValueError("'name' must be a non-empty string.")
        
        # Validate 'instance_krn' is a non-empty string
        if not isinstance(instance_krn, str) or not instance_krn.strip():
            raise ValueError("'instance_krn' must be a non-empty string.")
        
        # Validate 'x_region' is either In-Bangalore-1 or In-Hyderabad-1
        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")

        # Validate timeout
        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")
        
    def validate_list_image_parameters(
        self,
        *,
        region_id: str,
        
    ) -> None:
        """
        Validate the parameters before making the list_image request.

        Args:
        region_id: The region ID for the search.
        x_region: Optional region for advanced search.

        Raises:
        ValueError: If any of the required parameters are invalid.
        """

        # Check if region_id is provided and is a valid string
        if not region_id or not isinstance(region_id, str):
            raise ValueError("Invalid value for 'region_id'. It must be a non-empty string.")
        
        
    def validate_delete_image_parameters(
            self,
            *,
            snapshot_krn: str,
            extra_headers: Headers | None = None,
            extra_query: Query | None = None,
            extra_body: Body | None = None
        ) -> None:
            """
            Validate the parameters before making the DELETE request to delete an image.

            Args:
            snapshot_krn: The KRN of the image snapshot to delete.
            extra_headers: Optional extra headers to send with the request.
            extra_query: Optional extra query parameters.
            extra_body: Optional extra body data for the request.

            Raises:
            ValueError: If any of the required parameters are invalid.
            """

            # Check if snapshot_krn is provided and valid
            if not snapshot_krn or not isinstance(snapshot_krn, str):
                raise ValueError("Invalid value for 'snapshot_krn'. It must be a non-empty string.")

            # You can add additional checks for extra_headers, extra_query, and extra_body if needed
            if extra_headers is not None and not isinstance(extra_headers, dict):
                raise ValueError("Invalid value for 'extra_headers'. It must be a dictionary.")

            if extra_query is not None and not isinstance(extra_query, dict):
                raise ValueError("Invalid value for 'extra_query'. It must be a dictionary.")

            if extra_body is not None and not isinstance(extra_body, dict):
                raise ValueError("Invalid value for 'extra_body'. It must be a dictionary.")        

            


    def create_instance(
        self,
        *,
        image_krn: str,
        instanceName: str,
        instanceType: str,
        network_id: str,
        security_groups: List[str],
        sshkey_name: str,
        subnet_id: str,
        vm_volume_disk_size: str,
        vpc_id: str,
        x_region: str,
        floating_ip: bool | NotGiven = NOT_GIVEN,
        user_data: Union[str, Base64FileInput] | NotGiven = NOT_GIVEN,
        volume_name: Optional[str] | NotGiven = NOT_GIVEN,
        volume_size: int | NotGiven = NOT_GIVEN,
        volumetype: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | NotGiven = NOT_GIVEN,
        qos : dict,
        tags : List
    ) -> InstanceInfo:
        """
        Create a virtual machine instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        
        self.validate_create_instance_parameters(
            image_krn = image_krn,
            instanceName = instanceName,
            instanceType = instanceType,
            network_id = network_id,
            security_groups = security_groups,
            sshkey_name = sshkey_name,
            subnet_id = subnet_id,
            vm_volume_disk_size = vm_volume_disk_size ,
            vpc_id = vpc_id,
            floating_ip=floating_ip,
            user_data=user_data,
            volume_name=volume_name,
            volume_size=volume_size,
            volumetype=volumetype,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            qos=qos,
            tags=tags,
            x_region = x_region
         )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/v1/highlvlvpc/create_instance",
            body=maybe_transform(
                {
                    "image_krn": image_krn,
                    "instanceName": instanceName,
                    "instanceType": instanceType,
                    "network_id": network_id,
                    "sshkey_name": sshkey_name,
                    "subnet_id": subnet_id,
                    "vm_volume_disk_size": vm_volume_disk_size,
                    "vpc_id": vpc_id,
                    "floating_ip": floating_ip,
                    "security_groups" : security_groups,
                    "tags" : tags,
                    "user_data": user_data,
                    "volume_name": volume_name,
                    "volume_size": volume_size,
                    "volumetype": volumetype,
                    "timeout": timeout,
                    "qos": qos,
                    "region": x_region
                },
                highlvlvpc_create_instance_params.HighlvlvpcCreateInstanceParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InstanceInfo,
        )

    def create_port(
        self,
        *,
        floating_ip: bool,
        name: str,
        network_id: str,
        subnet_id: str,
        vpc_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PortDetail:
        """
        Create a network port and optionally attach a floating IP

        Args:
          floating_ip: Whether to allocate and associate a new floating IP to this port.

          name: Name for the new port.

          network_id: The KRN of the network to associate with the port.

          subnet_id: The KRN of the subnet to associate with the port and assign an IP from.

          vpc_id: The KRN of the VPC where the port will be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_create_port_parameters(
            floating_ip=floating_ip,
            name=name,
            network_id=network_id,
            subnet_id=subnet_id,
            vpc_id=vpc_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            x_region = x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/v1/highlvlvpc/create_port",
            body=maybe_transform(
                {
                    "floating_ip": floating_ip,
                    "name": name,
                    "network_id": network_id,
                    "subnet_id": subnet_id,
                    "vpc_id": vpc_id,
                },
                highlvlvpc_create_port_params.HighlvlvpcCreatePortParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PortDetail,
        )

    def create_subnet(
        self,
        *,
        subnet_data: highlvlvpc_create_subnet_params.SubnetData,
        vpc_id: str,
        router_krn : str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create a new subnet in the specified VPC

        Args:
          vpc_id: The ID of the VPC where the subnet will be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_create_subnet_parameters(
            subnet_data = subnet_data,
            vpc_id = vpc_id,
            router_krn = router_krn,
            extra_query = extra_query,
            extra_body = extra_body,
            timeout = timeout,
            x_region =x_region
        )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/v1/highlvlvpc/create_subnet",
            body=maybe_transform(
                {
                    "subnet_data": subnet_data,
                    "vpc_id": vpc_id,
                    "router_krn": router_krn
                },
                highlvlvpc_create_subnet_params.HighlvlvpcCreateSubnetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def create_vpc(
        self,
        *,
        network: dict,
        security_group: dict,
        security_group_rule: dict,
        subnet: dict,
        vpc: dict,
        x_region: str,
        # highlvlvpc_create_vpc_params.Vpc | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponse:
        """
        Create a new VPC along with network, subnet, router, and security group

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        
        self.validate_create_vpc_parameters(
            network = network,
            security_group = security_group,
            security_group_rule = security_group_rule,
            subnet = subnet,
            vpc = vpc,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            x_region = x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/v1/highlvlvpc/create_vpc_async",
            body=maybe_transform(
                {
                    "network": network,
                    "security_group": security_group,
                    "security_group_rule": security_group_rule,
                    "subnet": subnet,
                    "vpc": vpc,
                },
                highlvlvpc_create_vpc_params.HighlvlvpcCreateVpcParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponse,
        )

    def delete_instance(
        self,
        *,
        instanceKrn: str,
        deleteVolume : bool,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponse:
        """
        Delete a virtual machine instance

        Args:
          instance_krn: The KRN of the instance to be deleted.

          instance_name: The name of the instance to be deleted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_delete_instance_parameters(
            instanceKrn = instanceKrn,
            deleteVolume = deleteVolume,
            extra_headers= extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            x_region = x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/v1/highlvlvpc/delete_instance",
            body=maybe_transform(
                {
                    "instanceKrn": instanceKrn,
                    "deleteVolume": deleteVolume
                },
                highlvlvpc_delete_instance_params.HighlvlvpcDeleteInstanceParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponse,
        )

    def delete_vpc(
        self,
        *,
        vpc_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a VPC and its components

        Args:
          vpc_id: The ID of the VPC to delete.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """

        self.validate_delete_vpc_parameters(
            vpc_id = vpc_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            x_region = x_region
        )

        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._delete(
            "/v1/highlvlvpc/delete_vpc",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"vpc_id": vpc_id}, highlvlvpc_delete_vpc_params.HighlvlvpcDeleteVpcParams),
            ),
            cast_to=NoneType,
        )

    def get_vpc_task_status(
        self,
        *,
        task_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponse:
        """
        Get the status of a VPC creation task

        Args:
          task_id: The task ID of the VPC operation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_get_vpc_task_status_params(
            task_id = task_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            x_region = x_region
            )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/v1/highlvlvpc/get_vpc_task_status",
            body=maybe_transform(
                {"task_id": task_id}, highlvlvpc_get_vpc_task_status_params.HighlvlvpcGetVpcTaskStatusParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponse,
        )

    
    def list_instance_info(
        self,
        *,
        page: int  | None = None ,
        page_size: int |None = None,
        vpc_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InstanceInfoList:
        """
        Get a list of instance information

        Args:
          page: Page number for pagination.

          page_size: Number of instances per page.

          vpc_id: KRN of the VPC to filter instances.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_list_instance_info_parameters(
            vpc_id = vpc_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            page=page,
            page_size=page_size,
            x_region = x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._get(
            "/v1/highlvlvpc/instanceinfo",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                        "vpc_id": vpc_id,
                    },
                    highlvlvpc_list_instance_info_params.HighlvlvpcListInstanceInfoParams,
                ),
            ),
            cast_to=InstanceInfoList,
        )

    def list_vpcs(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        x_region: str,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HighlvlvpcListVpcsResponse:
        """
        List all VPCs for a customer

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._get(
            "/v1/highlvlvpc/get_vpc_list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HighlvlvpcListVpcsResponse,
        )

    def retrieve_instance(
        self,
        *,
        krn: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InstanceInfo:
        """
        Get instance information by KRN

        Args:
          krn: The KRN of the instance to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """

        self.validate_retrieve_instance_parameters(
            krn = krn,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            x_region = x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._get(
            "/v1/highlvlvpc/instance",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"krn": krn}, highlvlvpc_retrieve_instance_params.HighlvlvpcRetrieveInstanceParams
                ),
            ),
            cast_to=InstanceInfo,
        )

    def retrieve_vpc(
        self,
        *,
        vpc_id: Optional[str] | NotGiven = NOT_GIVEN,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VpcDetail:
        """
        Get VPC details by ID or name

        Args:
          vpc_id: The KRN of the VPC to retrieve.

          vpc_name: The name of the VPC to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/v1/highlvlvpc/get_vpc",
            body=maybe_transform(
                {
                    "vpc_id": vpc_id,
                },
                highlvlvpc_retrieve_vpc_params.HighlvlvpcRetrieveVpcParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VpcDetail,
        )

    
    def search_instances(
        self,
        *,
        vpc_id: str,
        x_region: str,
        x_user_email: Optional[str]| None | NotGiven = NOT_GIVEN ,
        limit: Optional[int] | None | NotGiven = NOT_GIVEN,
        page: Optional[int] | None | NotGiven = NOT_GIVEN,
        ip_fixed: Optional[str] | None | NotGiven = NOT_GIVEN,
        ip_floating: Optional[str] | None | NotGiven = NOT_GIVEN,
        krn: Optional[str] | None | NotGiven = NOT_GIVEN,
        name: Optional[str] | None | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InstanceInfoList:
        """
        Search for instances based on various criteria

        Args:
          vpc_id: The KRN of the VPC to filter instances.

          limit: Maximum number of instances to return per page.

          page: Page number for pagination.

          ip_fixed: Filter instances by fixed IP address.

          ip_floating: Filter instances by floating IP address.

          krn: Filter instances by their KRN.

          name: Filter instances by name (exact match or contains, depending on API).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """

        self.validate_search_instances_params(
            vpc_id = vpc_id,
            x_user_email = x_user_email,
            limit = limit,
            page= page,
            ip_fixed= ip_fixed,
            ip_floating = ip_floating,
            krn = krn,
            name = name,
            x_region = x_region
            )

        extra_headers = {
            "x-user-email": x_user_email,
            "vpc_id": vpc_id,
            "x-region": x_region,
            **(extra_headers or {}),
        }
        return self._get(
            "/v1/highlvlvpc/search_instances",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                        "vpc_id": vpc_id
                    },
                    highlvlvpc_search_instances_params.HighlvlvpcSearchInstancesParams,
                ),
            ),
            cast_to=InstanceInfoList,
        )
  
    def search_networks(
        self,
        *,
        vpc_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HighlvlvpcSearchNetworksResponse:
        """
        Search for networks within a VPC

        Args:
          vpc_id: The KRN of the VPC to search networks for.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
       

        self.validate_search_networks_parameters(
                vpc_id = vpc_id,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                x_region = x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._get(
            "/v1/highlvlvpc/search_network",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"vpc_id": vpc_id}, highlvlvpc_search_networks_params.HighlvlvpcSearchNetworksParams
                ),
            ),
            cast_to=HighlvlvpcSearchNetworksResponse,
        )
    
    
    def search_ports(
        self,
        *,
        x_region: str,
        name: str | NotGiven = NOT_GIVEN,
        network_id: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        port_id: str | NotGiven = NOT_GIVEN,
        size: int | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        vpc_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HighlvlvpcSearchPortsResponse:
        """
        Search for network ports based on various criteria

        Args:
          name: Filter ports by their name.

          network_id: Filter ports by KRN of the network.

          page: Page number for pagination.

          port_id: Filter ports by KRN of the port.

          size: Number of items to return per page.

          status: Filter ports by their status.

          vpc_id: Filter ports by VPC KRN.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._get(
            "/v1/highlvlvpc/search_port",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "name": name,
                        "network_id": network_id,
                        "page": page,
                        "port_id": port_id,
                        "size": size,
                        "status": status,
                        "vpc_id": vpc_id,
                    },
                    highlvlvpc_search_ports_params.HighlvlvpcSearchPortsParams,
                ),
            ),
            cast_to=HighlvlvpcSearchPortsResponse,
        )

    def search_vpcs(
        self,
        *,
        name: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        size: int | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HighlvlvpcSearchVpcsResponse:
        """
        Search for VPCs based on various criteria

        Args:
          name: Filter VPCs by name.

          page: Page number for pagination.

          size: Number of items to return per page.

          status: Filter VPCs by status.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/highlvlvpc/search_vpc",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "name": name,
                        "page": page,
                        "size": size,
                        "status": status,
                    },
                    highlvlvpc_search_vpcs_params.HighlvlvpcSearchVpcsParams,
                ),
            ),
            cast_to=HighlvlvpcSearchVpcsResponse,
        )
    def create_image(
        self,
        *,
        name: str,
        instance_krn: str,
        x_region: str,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
          
    ) -> HighlvlvpcCreateImageResponse:

        self.validate_create_image_parameters(
        name=name,
        instance_krn=instance_krn,
        x_region=x_region,
        
)

        extra_headers = {"x-region": x_region, **(extra_headers or {})}

        body = maybe_transform(
            {
                "name": name,
                "instance_krn": instance_krn,
            },
            highlvlvpc_create_image_params.HighlvlvpcCreateImageParams,
        )

        return self._post(
            f"/vm/v1/instance/createimage/{instance_krn}",
            body=body,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                
            ),
            cast_to=HighlvlvpcCreateImageResponse,
        )

    def list_image(
        self,
        *,
        region_id: str,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | NotGiven = NOT_GIVEN,
    ) -> HighlvlvpcListImageResponse:
        
        self.validate_list_image_parameters(
        region_id=region_id,
        
    )
        extra_headers = {**(extra_headers or {})}

        query = maybe_transform(
            {
                "region_id": region_id,
                "limit": limit,
                "page": page,
            },
            highlvlvpc_list_image_params.HighlvlvpcListImageParams,
        )

        return self._get(
            f"/vm/v1/image/{region_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=query,
            ),
            cast_to=HighlvlvpcListImageResponse,
        )

    def delete_image(
        self,
        *,
        snapshot_krn: str,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
    ) -> None:
        self.validate_delete_image_parameters(
            snapshot_krn=snapshot_krn,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            
        )
        
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
    
        query = maybe_transform(
            {"snapshot_krn": snapshot_krn},
            highlvlvpc_delete_image_params.HighlvlvpcDeleteImageParams,
        )

        return self._delete(
            f"/vm/v1/image/{snapshot_krn}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                query=query,
            ),
            cast_to=NoneType,  
        )


class AsyncHighlvlvpcResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncHighlvlvpcResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.
        """
        return AsyncHighlvlvpcResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHighlvlvpcResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.
        """
        return AsyncHighlvlvpcResourceWithStreamingResponse(self)

    async def validate_create_subnet_parameters(
    self,
    subnet_data,
    vpc_id,
    router_krn,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        if not isinstance(subnet_data, dict):
            raise ValueError("'subnet_data' must be a dictionary.")

        required_fields = ["cidr", "ip_version", "name"]
        for field in required_fields:
            if field not in subnet_data:
                raise ValueError(f"'{field}' is required in subnet_data.")
        
        if not isinstance(subnet_data["cidr"], str):
            raise ValueError("'cidr' must be a string.")
        
        if subnet_data["ip_version"] not in (4, 6):
            raise ValueError("'ip_version' must be either 4 or 6.")
        
        if not isinstance(subnet_data["name"], str):
            raise ValueError("'name' must be a string.")

        if "description" in subnet_data and not isinstance(subnet_data["description"], str):
            raise ValueError("'description' must be a string if provided.")

        if "gateway_ip" in subnet_data and not isinstance(subnet_data["gateway_ip"], str):
            raise ValueError("'gateway_ip' must be a string if provided.")

        if not isinstance(vpc_id, str):
            raise ValueError("'vpc_id' must be a string.")
        
        if not isinstance(router_krn, str):
            raise ValueError("'router_krn' must be a string.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")


    

    async def validate_create_instance_parameters(
    self,
    image_krn,
    instanceName,
    instanceType,
    network_id,
    security_groups,
    sshkey_name,
    subnet_id,
    vm_volume_disk_size,
    vpc_id,
    x_region,
    floating_ip=None,
    user_data=None,
    volume_name=None,
    volume_size=None,
    volumetype=None,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None,
    qos=None,
    tags=None
    ):
        # Required string parameters
        for name, value in {
            "image_krn": image_krn,
            "instanceName": instanceName,
            "instanceType": instanceType,
            "network_id": network_id,
            "sshkey_name": sshkey_name,
            "subnet_id": subnet_id,
            "vm_volume_disk_size": vm_volume_disk_size,
            "vpc_id": vpc_id,
            "volumetype": volumetype,
        }.items():
            if not isinstance(value, str) or not value:
                raise ValueError(f"'{name}' must be a non-empty string.")

        # Optional: floating_ip
        if floating_ip is not None and not isinstance(floating_ip, bool):
            raise ValueError("'floating_ip' must be a boolean if provided.")

        # Optional: user_data
        if user_data is not None and not isinstance(user_data, (str, dict)):
            raise ValueError("'user_data' must be a string or Base64FileInput (dict) if provided.")

        # Optional: volume_name
        if volume_name is not None and not isinstance(volume_name, str):
            raise ValueError("'volume_name' must be a string if provided.")

        # Optional: volume_size
        if volume_size is not None and not isinstance(volume_size, int):
            raise ValueError("'volume_size' must be an integer if provided.")

        # Optional: extra dicts
        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")
        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")
        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        # Optional: timeout
        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        # qos
        if not isinstance(qos, dict):
            raise ValueError("'qos' must be a dictionary.")

        # tags
        if not isinstance(tags, list):
            raise ValueError("'tags' must be a list.")

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



    async def validate_create_vpc_parameters(
    self,
    network: dict,
    security_group: dict,
    security_group_rule: dict,
    subnet: dict,
    vpc: dict,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
        ):
        # --- network ---
        if not isinstance(network, dict):
            raise ValueError("'network' must be a dictionary.")
        if "name" not in network or not isinstance(network["name"], str):
            raise ValueError("'network.name' must be a non-empty string.")
        if "admin_state_up" not in network or not isinstance(network["admin_state_up"], bool):
            raise ValueError("'network.admin_state_up' must be a boolean.")

        # --- security_group ---
        if not isinstance(security_group, dict):
            raise ValueError("'security_group' must be a dictionary.")
        if "name" not in security_group or not isinstance(security_group["name"], str):
            raise ValueError("'security_group.name' must be a string.")
        if "description" not in security_group or not isinstance(security_group["description"], str):
            raise ValueError("'security_group.description' must be a string.")

        # --- security_group_rule ---
        if not isinstance(security_group_rule, dict):
            raise ValueError("'security_group_rule' must be a dictionary.")
        if security_group_rule.get("direction") not in ("ingress", "egress"):
            raise ValueError("'security_group_rule.direction' must be 'ingress' or 'egress'.")
        if security_group_rule.get("ethertypes") not in ("IPv4", "IPv6"):
            raise ValueError("'security_group_rule.ethertypes' must be 'IPv4' or 'IPv6'.")
        if not isinstance(security_group_rule.get("protocol"), str):
            raise ValueError("'security_group_rule.protocol' must be a string.")
        if not isinstance(security_group_rule.get("portMinRange"), int):
            raise ValueError("'security_group_rule.portMinRange' must be an integer.")
        if not isinstance(security_group_rule.get("portMaxRange"), int):
            raise ValueError("'security_group_rule.portMaxRange' must be an integer.")
        if not isinstance(security_group_rule.get("remoteIPPrefix"), str):
            raise ValueError("'security_group_rule.remoteIPPrefix' must be a string.")

        # --- subnet ---
        if not isinstance(subnet, dict):
            raise ValueError("'subnet' must be a dictionary.")
        for key in ("cidr", "gateway_ip", "name", "description"):
            if key not in subnet or not isinstance(subnet[key], str):
                raise ValueError(f"'subnet.{key}' must be a string.")
        if subnet.get("ip_version") not in (4, 6):
            raise ValueError("'subnet.ip_version' must be 4 or 6.")
        if not isinstance(subnet.get("ingress"), bool):
            raise ValueError("'subnet.ingress' must be a boolean.")
        if not isinstance(subnet.get("egress"), bool):
            raise ValueError("'subnet.egress' must be a boolean.")

        # --- vpc ---
        if not isinstance(vpc, dict):
            raise ValueError("'vpc' must be a dictionary.")
        if "name" not in vpc or not isinstance(vpc["name"], str):
            raise ValueError("'vpc.name' must be a string.")
        if "description" not in vpc or not isinstance(vpc["description"], str):
            raise ValueError("'vpc.description' must be a string.")
        if "enabled" not in vpc or not isinstance(vpc["enabled"], bool):
            raise ValueError("'vpc.enabled' must be a boolean.")

        # --- optional extras ---
        for name, param in {
            "extra_headers": extra_headers,
            "extra_query": extra_query,
            "extra_body": extra_body,
        }.items():
            if param is not None and not isinstance(param, dict):
                raise ValueError(f"'{name}' must be a dictionary if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")

    async def validate_delete_instance_parameters(
    self,
    instanceKrn: str,
    deleteVolume: bool,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        # Validate instanceKrn
        if not isinstance(instanceKrn, str) or not instanceKrn.strip():
            raise ValueError("'instanceKrn' must be a non-empty string.")

        # Validate deleteVolume
        if not isinstance(deleteVolume, bool):
            raise ValueError("'deleteVolume' must be a boolean.")

        # Validate extra headers/query/body if provided
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

    

  
    async def validate_delete_vpc_parameters(
    self,
    vpc_id: str,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        # Validate 'vpc_id'
        if not isinstance(vpc_id, str) or not vpc_id.strip():
            raise ValueError("'vpc_id' must be a non-empty string.")

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


    async def validate_list_instance_info_parameters(
    self,
    vpc_id: str,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None,
    page=None,
    page_size=None
    ):
        # Validate 'vpc_id'
        if not isinstance(vpc_id, str) or not vpc_id.strip():
            raise ValueError("'vpc_id' must be a non-empty string.")

        # Validate 'page' if provided
        if page is not None:
            if not isinstance(page, int) or page < 1:
                raise ValueError("'page' must be a positive integer if provided.")

        # Validate 'page_size' if provided
        if page_size is not None:
            if not isinstance(page_size, int) or page_size < 1:
                raise ValueError("'page_size' must be a positive integer if provided.")

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


    async def validate_retrieve_instance_parameters(
    self,
    krn: str,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        if not isinstance(krn, str) or not krn.strip():
            raise ValueError("'krn' must be a non-empty string.")

        for name, param in {
            "extra_headers": extra_headers,
            "extra_query": extra_query,
            "extra_body": extra_body,
        }.items():
            if param is not None and not isinstance(param, dict):
                raise ValueError(f"'{name}' must be a dictionary if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")
        
        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")


    async def validate_get_vpc_task_status_params(
    self,
    task_id: str,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("'task_id' must be a non-empty string.")

        for name, param in {
            "extra_headers": extra_headers,
            "extra_query": extra_query,
            "extra_body": extra_body,
        }.items():
            if param is not None and not isinstance(param, dict):
                raise ValueError(f"'{name}' must be a dict if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")
        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")


    async def validate_search_instances_params(
    self,
    vpc_id: str,
    x_region,
    x_user_email = NOT_GIVEN,
    limit = NOT_GIVEN,
    page = NOT_GIVEN,
    ip_fixed = NOT_GIVEN,
    ip_floating = NOT_GIVEN,
    krn = NOT_GIVEN,
    name = NOT_GIVEN
    ):
        if not isinstance(vpc_id, str) or not vpc_id.strip():
            raise ValueError("vpc_id must be a non-empty string.")
        
        if x_user_email is not NOT_GIVEN and x_user_email is not None:
            if not isinstance(x_user_email, str) or "@" not in x_user_email:
                raise ValueError("x_user_email must be a valid email string.")
        
        if limit is not NOT_GIVEN and limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                raise ValueError("limit must be a positive integer.")

        if page is not NOT_GIVEN and page is not None:
            if not isinstance(page, int) or page <= 0:
                raise ValueError("page must be a positive integer.")

        def _validate_ip(ip):
            if ip is not NOT_GIVEN and ip is not None:
                if not isinstance(ip, str) or not ip:
                    raise ValueError("IP address must be a non-empty string.")

        _validate_ip(ip_fixed)
        _validate_ip(ip_floating)

        if krn is not NOT_GIVEN and krn is not None:
            if not isinstance(krn, str) or not krn.strip():
                raise ValueError("krn must be a non-empty string if provided.")
        
        if name is not NOT_GIVEN and name is not None:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("name must be a non-empty string if provided.")
        
        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")



    async def validate_search_networks_parameters(
    self,
    vpc_id,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        # Required: vpc_id must be a non-empty string
        if not isinstance(vpc_id, str) or not vpc_id:
            raise ValueError("'vpc_id' must be a non-empty string.")

        # Optional: extra_headers must be a dictionary if provided
        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")

        # Optional: extra_query must be a dictionary if provided
        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")

        # Optional: extra_body must be a dictionary if provided
        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        # Optional: timeout must be float/int/httpx.Timeout if provided
        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (float, int, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")
        
        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")
    
    async def validate_create_port_parameters(
        self,
        *,
        floating_ip,
        name,
        network_id,
        subnet_id,
        vpc_id,
        x_region,
        extra_headers=None,
        extra_query=None,
        extra_body=None,
        timeout=None
        ):
            # Required: floating_ip must be a boolean
            if not isinstance(floating_ip, bool):
                raise ValueError("'floating_ip' must be a boolean.")

            # Required string parameters
            for param_name, param_value in {
                "name": name,
                "network_id": network_id,
                "subnet_id": subnet_id,
                "vpc_id": vpc_id,
            }.items():
                if not isinstance(param_value, str) or not param_value:
                    raise ValueError(f"'{param_name}' must be a non-empty string.")

            # Optional: extra_headers must be a dictionary if provided
            if extra_headers is not None and not isinstance(extra_headers, dict):
                raise ValueError("'extra_headers' must be a dictionary if provided.")

            # Optional: extra_query must be a dictionary if provided
            if extra_query is not None and not isinstance(extra_query, dict):
                raise ValueError("'extra_query' must be a dictionary if provided.")

            # Optional: extra_body must be a dictionary if provided
            if extra_body is not None and not isinstance(extra_body, dict):
                raise ValueError("'extra_body' must be a dictionary if provided.")

            # Optional: timeout must be float/int/httpx.Timeout if provided
            if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (float, int, httpx.Timeout)):
                raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

            if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
                raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")

    async def validate_create_image_parameters(
        self,
        name: str,
        instance_krn: str,
        x_region: str,
        timeout: float | NotGiven = NOT_GIVEN
    ):
        # Validate 'name' is a non-empty string
        if not isinstance(name, str) or not name.strip():
            raise ValueError("'name' must be a non-empty string.")
        
        # Validate 'instance_krn' is a non-empty string
        if not isinstance(instance_krn, str) or not instance_krn.strip():
            raise ValueError("'instance_krn' must be a non-empty string.")
        
        # Validate 'x_region' is either In-Bangalore-1 or In-Hyderabad-1
        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")

        # Validate timeout
        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")
        
    async def validate_list_image_parameters(
        self,
        *,
        region_id: str,
        
    ) -> None:
        """
        Validate the parameters before making the list_image request.

        Args:
        region_id: The region ID for the search.
        x_region: Optional region for advanced search.

        Raises:
        ValueError: If any of the required parameters are invalid.
        """

        # Check if region_id is provided and is a valid string
        if not region_id or not isinstance(region_id, str):
            raise ValueError("Invalid value for 'region_id'. It must be a non-empty string.")
        
    async def validate_delete_image_parameters(
            self,
            *,
            snapshot_krn: str,
            extra_headers: Headers | None = None,
            extra_query: Query | None = None,
            extra_body: Body | None = None
        ) -> None:
            """
            Validate the parameters before making the DELETE request to delete an image.

            Args:
            snapshot_krn: The KRN of the image snapshot to delete.
            extra_headers: Optional extra headers to send with the request.
            extra_query: Optional extra query parameters.
            extra_body: Optional extra body data for the request.

            Raises:
            ValueError: If any of the required parameters are invalid.
            """

            # Check if snapshot_krn is provided and valid
            if not snapshot_krn or not isinstance(snapshot_krn, str):
                raise ValueError("Invalid value for 'snapshot_krn'. It must be a non-empty string.")

            # You can add additional checks for extra_headers, extra_query, and extra_body if needed
            if extra_headers is not None and not isinstance(extra_headers, dict):
                raise ValueError("Invalid value for 'extra_headers'. It must be a dictionary.")

            if extra_query is not None and not isinstance(extra_query, dict):
                raise ValueError("Invalid value for 'extra_query'. It must be a dictionary.")

            if extra_body is not None and not isinstance(extra_body, dict):
                raise ValueError("Invalid value for 'extra_body'. It must be a dictionary.")     
  

    async def create_instance(
        self,
        *,
        image_krn: str,
        instanceName: str,
        instanceType: str,
        network_id: str,
        security_groups: List[str],
        sshkey_name: str,
        subnet_id: str,
        vm_volume_disk_size: str,
        vpc_id: str,
        x_region: str,
        floating_ip: bool | NotGiven = NOT_GIVEN,
        security_group_rules_name: str | NotGiven = NOT_GIVEN,
        security_group_rules_port: str | NotGiven = NOT_GIVEN,
        security_group_rules_protocol: str | NotGiven = NOT_GIVEN,
        user_data: Union[str, Base64FileInput] | NotGiven = NOT_GIVEN,
        volume_name: Optional[str] | NotGiven = NOT_GIVEN,
        volume_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        qos: dict,
        tags: List
    ) -> InstanceInfo:
        """
        Create a virtual machine instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_create_instance_parameters(
            image_krn = image_krn,
            instanceName = instanceName,
            instanceType = instanceType,
            network_id = network_id,
            security_groups = security_groups,
            sshkey_name = sshkey_name,
            subnet_id = subnet_id,
            vm_volume_disk_size = vm_volume_disk_size ,
            vpc_id = vpc_id,
            floating_ip=floating_ip,
            user_data=user_data,
            volume_name=volume_name,
            volume_size=volume_size,
            volumetype=volumetype,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            qos=qos,
            tags=tags,
            x_region = x_region
         )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/v1/highlvlvpc/create_instance",
            body=await async_maybe_transform(
                {
                    "image_krn": image_krn,
                    "instanceName": instanceName,
                    "instanceType": instanceType,
                    "network_id": network_id,
                    "security_groups": security_groups,
                    "sshkey_name": sshkey_name,
                    "subnet_id": subnet_id,
                    "vm_volume_disk_size": vm_volume_disk_size,
                    "vpc_id": vpc_id,
                    "floating_ip": floating_ip,
                    "security_group_rules_name": security_group_rules_name,
                    "security_group_rules_port": security_group_rules_port,
                    "security_group_rules_protocol": security_group_rules_protocol,
                    "user_data": user_data,
                    "volume_name": volume_name,
                    "volume_size": volume_size,
                    "timeout": timeout,
                    "qos": qos,
                    "region": x_region
                },
                highlvlvpc_create_instance_params.HighlvlvpcCreateInstanceParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InstanceInfo,
        )

    async def create_port(
        self,
        *,
        floating_ip: bool,
        name: str,
        network_id: str,
        subnet_id: str,
        vpc_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PortDetail:
        """
        Create a network port and optionally attach a floating IP

        Args:
          floating_ip: Whether to allocate and associate a new floating IP to this port.

          name: Name for the new port.

          network_id: The KRN of the network to associate with the port.

          subnet_id: The KRN of the subnet to associate with the port and assign an IP from.

          vpc_id: The KRN of the VPC where the port will be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        
        await self.validate_create_port_parameters(
            floating_ip=floating_ip,
            name=name,
            network_id=network_id,
            subnet_id=subnet_id,
            vpc_id=vpc_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/v1/highlvlvpc/create_port",
            body=await async_maybe_transform(
                {
                    "floating_ip": floating_ip,
                    "name": name,
                    "network_id": network_id,
                    "subnet_id": subnet_id,
                    "vpc_id": vpc_id,
                },
                highlvlvpc_create_port_params.HighlvlvpcCreatePortParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PortDetail,
        )

    async def create_subnet(
        self,
        *,
        subnet_data: highlvlvpc_create_subnet_params.SubnetData,
        vpc_id: str,
        router_krn: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create a new subnet in the specified VPC

        Args:
          vpc_id: The ID of the VPC where the subnet will be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_create_subnet_parameters(
            subnet_data = subnet_data,
            vpc_id = vpc_id,
            router_krn = router_krn,
            extra_query = extra_query,
            extra_body = extra_body,
            timeout = timeout
        )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/v1/highlvlvpc/create_subnet",
            body=await async_maybe_transform(
                {
                    "subnet_data": subnet_data,
                    "vpc_id": vpc_id,
                    "router_krn": router_krn
                },
                highlvlvpc_create_subnet_params.HighlvlvpcCreateSubnetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def create_vpc(
       self,
        *,
        network: dict,
        security_group: dict,
        security_group_rule: dict,
        subnet: dict,
        vpc: dict,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponse:
        """
        Create a new VPC along with network, subnet, router, and security group

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_create_vpc_parameters(
            network = network,
            security_group = security_group,
            security_group_rule = security_group_rule,
            subnet = subnet,
            vpc = vpc,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/v1/highlvlvpc/create_vpc_async",
            body=await async_maybe_transform(
                {
                    "network": network,
                    "security_group": security_group,
                    "security_group_rule": security_group_rule,
                    "subnet": subnet,
                    "vpc": vpc,
                },
                highlvlvpc_create_vpc_params.HighlvlvpcCreateVpcParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponse,
        )

    async def delete_instance(
        self,
        *,
        instanceKrn: str,
        deleteVolume : bool,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponse:
        """
        Delete a virtual machine instance

        Args:
          instance_krn: The KRN of the instance to be deleted.

          instance_name: The name of the instance to be deleted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_delete_instance_parameters(
            instanceKrn = instanceKrn,
            deleteVolume = deleteVolume,
            extra_headers= extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/v1/highlvlvpc/delete_instance",
            body=await async_maybe_transform(
                {
                    "instance_krn": instance_krn,
                    "instance_name": instance_name,
                },
                highlvlvpc_delete_instance_params.HighlvlvpcDeleteInstanceParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponse,
        )

    async def delete_vpc(
        self,
        *,
        vpc_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a VPC and its components

        Args:
          vpc_id: The ID of the VPC to delete.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_delete_vpc_parameters(
            vpc_id = vpc_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._delete(
            "/v1/highlvlvpc/delete_vpc",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"vpc_id": vpc_id}, highlvlvpc_delete_vpc_params.HighlvlvpcDeleteVpcParams
                ),
            ),
            cast_to=NoneType,
        )

    async def get_vpc_task_status(
        self,
        *,
        task_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponse:
        """
        Get the status of a VPC creation task

        Args:
          task_id: The task ID of the VPC operation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_get_vpc_task_status_params(
            task_id = task_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/v1/highlvlvpc/get_vpc_task_status",
            body=await async_maybe_transform(
                {"task_id": task_id}, highlvlvpc_get_vpc_task_status_params.HighlvlvpcGetVpcTaskStatusParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponse,
        )

    
    async def list_instance_info(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        vpc_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InstanceInfoList:
        """
        Get a list of instance information

        Args:
          page: Page number for pagination.

          page_size: Number of instances per page.

          vpc_id: KRN of the VPC to filter instances.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_list_instance_info_parameters(
            vpc_id = vpc_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            page=page,
            page_size=page_size,
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._get(
            "/v1/highlvlvpc/instanceinfo",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                        "vpc_id": vpc_id,
                    },
                    highlvlvpc_list_instance_info_params.HighlvlvpcListInstanceInfoParams,
                ),
            ),
            cast_to=InstanceInfoList,
        )

    async def list_vpcs(
        self,
        *,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HighlvlvpcListVpcsResponse:
        """
        List all VPCs for a customer

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._get(
            "/v1/highlvlvpc/get_vpc_list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HighlvlvpcListVpcsResponse,
        )

    async def retrieve_instance(
        self,
        *,
        krn: str,
        x_region : str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InstanceInfo:
        """
        Get instance information by KRN

        Args:
          krn: The KRN of the instance to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_retrieve_instance_parameters(
            krn = krn,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._get(
            "/v1/highlvlvpc/instance",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"krn": krn}, highlvlvpc_retrieve_instance_params.HighlvlvpcRetrieveInstanceParams
                ),
            ),
            cast_to=InstanceInfo,
        )

    async def retrieve_vpc(
        self,
        *,
        vpc_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VpcDetail:
        """
        Get VPC details by ID or name

        Args:
          vpc_id: The KRN of the VPC to retrieve.

          vpc_name: The name of the VPC to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/v1/highlvlvpc/get_vpc",
            body=await async_maybe_transform(
                {
                    "vpc_id": vpc_id,
                },
                highlvlvpc_retrieve_vpc_params.HighlvlvpcRetrieveVpcParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VpcDetail,
        )

    

    async def search_instances(
        self,
        *,
        vpc_id: str,
        x_region: str,
        x_user_email: str| NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        ip_fixed: Optional[str] | NotGiven = NOT_GIVEN,
        ip_floating: Optional[str] | NotGiven = NOT_GIVEN,
        krn: Optional[str] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InstanceInfoList:
        """
        Search for instances based on various criteria

        Args:
          vpc_id: The KRN of the VPC to filter instances.

          limit: Maximum number of instances to return per page.

          page: Page number for pagination.

          ip_fixed: Filter instances by fixed IP address.

          ip_floating: Filter instances by floating IP address.

          krn: Filter instances by their KRN.

          name: Filter instances by name (exact match or contains, depending on API).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """


        await self.validate_search_instances_params(
            vpc_id = vpc_id,
            x_user_email = x_user_email,
            limit = limit,
            page= page,
            ip_fixed= ip_fixed,
            ip_floating = ip_floating,
            krn = krn,
            name = name,
            )

        extra_headers = {
            "x-user-email": x_user_email,
            "vpc_id": vpc_id,
            "x-region": x_region,
            **(extra_headers or {}),
        }
        return await self._post(
            "/v1/highlvlvpc/search_instances",
            body=await async_maybe_transform(
                {
                    "vpc_id": vpc_id,
                    "ip_fixed": ip_fixed,
                    "ip_floating": ip_floating,
                    "krn": krn,
                    "name": name,
                },
                highlvlvpc_search_instances_params.HighlvlvpcSearchInstancesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                    },
                    highlvlvpc_search_instances_params.HighlvlvpcSearchInstancesParams,
                ),
            ),
            cast_to=InstanceInfoList,
        )
    

   

   

   

    async def search_networks(
        self,
        *,
        vpc_id: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HighlvlvpcSearchNetworksResponse:
        """
        Search for networks within a VPC

        Args:
          vpc_id: The KRN of the VPC to search networks for.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_search_networks_parameters(
                vpc_id = vpc_id,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                x_region = x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._get(
            "/v1/highlvlvpc/search_network",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"vpc_id": vpc_id}, highlvlvpc_search_networks_params.HighlvlvpcSearchNetworksParams
                ),
            ),
            cast_to=HighlvlvpcSearchNetworksResponse,
        )

    async def search_ports(
        self,
        *,
        x_region: str,
        name: str | NotGiven = NOT_GIVEN,
        network_id: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        port_id: str | NotGiven = NOT_GIVEN,
        size: int | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        vpc_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HighlvlvpcSearchPortsResponse:
        """
        Search for network ports based on various criteria

        Args:
          name: Filter ports by their name.

          network_id: Filter ports by KRN of the network.

          page: Page number for pagination.

          port_id: Filter ports by KRN of the port.

          size: Number of items to return per page.

          status: Filter ports by their status.

          vpc_id: Filter ports by VPC KRN.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._get(
            "/v1/highlvlvpc/search_port",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "name": name,
                        "network_id": network_id,
                        "page": page,
                        "port_id": port_id,
                        "size": size,
                        "status": status,
                        "vpc_id": vpc_id,
                    },
                    highlvlvpc_search_ports_params.HighlvlvpcSearchPortsParams,
                ),
            ),
            cast_to=HighlvlvpcSearchPortsResponse,
        )

    async def search_vpcs(
        self,
        *,
        name: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        size: int | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HighlvlvpcSearchVpcsResponse:
        """
        Search for VPCs based on various criteria

        Args:
          name: Filter VPCs by name.

          page: Page number for pagination.

          size: Number of items to return per page.

          status: Filter VPCs by status.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/highlvlvpc/search_vpc",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "name": name,
                        "page": page,
                        "size": size,
                        "status": status,
                    },
                    highlvlvpc_search_vpcs_params.HighlvlvpcSearchVpcsParams,
                ),
            ),
            cast_to=HighlvlvpcSearchVpcsResponse,
        )

    async def create_image(
        self,
        *,
        name: str,
        instance_krn: str,
        x_region: str,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
          
    ) -> HighlvlvpcCreateImageResponse:

        self.validate_create_image_parameters(
        name=name,
        instance_krn=instance_krn,
        x_region=x_region,
        
)

        extra_headers = {"x-region": x_region, **(extra_headers or {})}

        body = maybe_transform(
            {
                "name": name,
                "instance_krn": instance_krn,
            },
            highlvlvpc_create_image_params.HighlvlvpcCreateImageParams,
        )

        return self._post(
            f"/vm/v1/instance/createimage/{instance_krn}",
            body=body,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                
            ),
            cast_to=HighlvlvpcCreateImageResponse,
        )

    async def list_image(
        self,
        *,
        region_id: str,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | NotGiven = NOT_GIVEN,
    ) -> HighlvlvpcListImageResponse:
        
        self.validate_list_image_parameters(
        region_id=region_id,
        
    )

        extra_headers = {**(extra_headers or {})}

        query = maybe_transform(
            {
                "region_id": region_id,
                "limit": limit,
                "page": page,
            },
            highlvlvpc_list_image_params.HighlvlvpcListImageParams,
        )

        return self._get(
            f"/vm/v1/image/{region_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=query,
            ),
            cast_to=HighlvlvpcListImageResponse,
        )

    async def delete_image(
        self,
        *,
        snapshot_krn: str,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
    ) -> None:
        
        self.validate_delete_image_parameters(
            snapshot_krn=snapshot_krn,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            
        )

        extra_headers = {"Accept": "*/*", **(extra_headers or {})}

        query = maybe_transform(
            {"snapshot_krn": snapshot_krn},
            highlvlvpc_delete_image_params.HighlvlvpcDeleteImageParams,
        )

        return self._delete(
            f"/vm/v1/image/{snapshot_krn}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                query=query,
            ),
            cast_to=NoneType,  
        )
    


class HighlvlvpcResourceWithRawResponse:
    def __init__(self, highlvlvpc: HighlvlvpcResource) -> None:
        self._highlvlvpc = highlvlvpc

        self.create_instance = to_raw_response_wrapper(
            highlvlvpc.create_instance,
        )
        self.create_port = to_raw_response_wrapper(
            highlvlvpc.create_port,
        )
        self.create_subnet = to_raw_response_wrapper(
            highlvlvpc.create_subnet,
        )
        self.create_vpc = to_raw_response_wrapper(
            highlvlvpc.create_vpc,
        )
        self.delete_instance = to_raw_response_wrapper(
            highlvlvpc.delete_instance,
        )
        self.delete_vpc = to_raw_response_wrapper(
            highlvlvpc.delete_vpc,
        )
        self.get_vpc_task_status = to_raw_response_wrapper(
            highlvlvpc.get_vpc_task_status,
        )
        self.list_instance_info = to_raw_response_wrapper(
            highlvlvpc.list_instance_info,
        )
        self.list_vpcs = to_raw_response_wrapper(
            highlvlvpc.list_vpcs,
        )
        self.retrieve_instance = to_raw_response_wrapper(
            highlvlvpc.retrieve_instance,
        )
        self.retrieve_vpc = to_raw_response_wrapper(
            highlvlvpc.retrieve_vpc,
        )
        self.search_instances = to_raw_response_wrapper(
            highlvlvpc.search_instances,
        )
        self.search_networks = to_raw_response_wrapper(
            highlvlvpc.search_networks,
        )
        self.search_ports = to_raw_response_wrapper(
            highlvlvpc.search_ports,
        )
        self.search_vpcs = to_raw_response_wrapper(
            highlvlvpc.search_vpcs,
        )
        self.create_image = to_raw_response_wrapper(
            highlvlvpc.create_image,
        )
        self.list_image = to_raw_response_wrapper(
            highlvlvpc.list_image,
        )
        self.delete_image = to_raw_response_wrapper(
            highlvlvpc.delete_image
            
        )

class AsyncHighlvlvpcResourceWithRawResponse:
    def __init__(self, highlvlvpc: AsyncHighlvlvpcResource) -> None:
        self._highlvlvpc = highlvlvpc

        self.create_instance = async_to_raw_response_wrapper(
            highlvlvpc.create_instance,
        )
        self.create_port = async_to_raw_response_wrapper(
            highlvlvpc.create_port,
        )
        self.create_subnet = async_to_raw_response_wrapper(
            highlvlvpc.create_subnet,
        )
        self.create_vpc = async_to_raw_response_wrapper(
            highlvlvpc.create_vpc,
        )
        self.delete_instance = async_to_raw_response_wrapper(
            highlvlvpc.delete_instance,
        )
        self.delete_vpc = async_to_raw_response_wrapper(
            highlvlvpc.delete_vpc,
        )
        self.get_vpc_task_status = async_to_raw_response_wrapper(
            highlvlvpc.get_vpc_task_status,
        )
        self.list_instance_info = async_to_raw_response_wrapper(
            highlvlvpc.list_instance_info,
        )
        self.list_vpcs = async_to_raw_response_wrapper(
            highlvlvpc.list_vpcs,
        )
        self.retrieve_instance = async_to_raw_response_wrapper(
            highlvlvpc.retrieve_instance,
        )
        self.retrieve_vpc = async_to_raw_response_wrapper(
            highlvlvpc.retrieve_vpc,
        )
        self.search_instances = async_to_raw_response_wrapper(
            highlvlvpc.search_instances,
        )
        self.search_networks = async_to_raw_response_wrapper(
            highlvlvpc.search_networks,
        )
        self.search_ports = async_to_raw_response_wrapper(
            highlvlvpc.search_ports,
        )
        self.search_vpcs = async_to_raw_response_wrapper(
            highlvlvpc.search_vpcs,
        )
        self.create_image = async_to_raw_response_wrapper(
            highlvlvpc.create_image,
        )
        self.list_image = async_to_raw_response_wrapper(
            highlvlvpc.list_image,
        )
        self.delete_image = async_to_raw_response_wrapper(
            highlvlvpc.delete_image
            
        )



class HighlvlvpcResourceWithStreamingResponse:
    def __init__(self, highlvlvpc: HighlvlvpcResource) -> None:
        self._highlvlvpc = highlvlvpc

        self.create_instance = to_streamed_response_wrapper(
            highlvlvpc.create_instance,
        )
        self.create_port = to_streamed_response_wrapper(
            highlvlvpc.create_port,
        )
        self.create_subnet = to_streamed_response_wrapper(
            highlvlvpc.create_subnet,
        )
        self.create_vpc = to_streamed_response_wrapper(
            highlvlvpc.create_vpc,
        )
        self.delete_instance = to_streamed_response_wrapper(
            highlvlvpc.delete_instance,
        )
        self.delete_vpc = to_streamed_response_wrapper(
            highlvlvpc.delete_vpc,
        )
        self.get_vpc_task_status = to_streamed_response_wrapper(
            highlvlvpc.get_vpc_task_status,
        )
        self.list_instance_info = to_streamed_response_wrapper(
            highlvlvpc.list_instance_info,
        )
        self.list_vpcs = to_streamed_response_wrapper(
            highlvlvpc.list_vpcs,
        )
        self.retrieve_instance = to_streamed_response_wrapper(
            highlvlvpc.retrieve_instance,
        )
        self.retrieve_vpc = to_streamed_response_wrapper(
            highlvlvpc.retrieve_vpc,
        )
        self.search_instances = to_streamed_response_wrapper(
            highlvlvpc.search_instances,
        )
        self.search_networks = to_streamed_response_wrapper(
            highlvlvpc.search_networks,
        )
        self.search_ports = to_streamed_response_wrapper(
            highlvlvpc.search_ports,
        )
        self.search_vpcs = to_streamed_response_wrapper(
            highlvlvpc.search_vpcs,
        )
        self.create_image = to_streamed_response_wrapper(
            highlvlvpc.create_image,
        )
        self.list_image = to_streamed_response_wrapper(
            highlvlvpc.list_image,
        )
        self.delete_image = to_streamed_response_wrapper(
            highlvlvpc.delete_image
            
        )




class AsyncHighlvlvpcResourceWithStreamingResponse:
    def __init__(self, highlvlvpc: AsyncHighlvlvpcResource) -> None:
        self._highlvlvpc = highlvlvpc

        self.create_instance = async_to_streamed_response_wrapper(
            highlvlvpc.create_instance,
        )
        self.create_port = async_to_streamed_response_wrapper(
            highlvlvpc.create_port,
        )
        self.create_subnet = async_to_streamed_response_wrapper(
            highlvlvpc.create_subnet,
        )
        self.create_vpc = async_to_streamed_response_wrapper(
            highlvlvpc.create_vpc,
        )
        self.delete_instance = async_to_streamed_response_wrapper(
            highlvlvpc.delete_instance,
        )
        self.delete_vpc = async_to_streamed_response_wrapper(
            highlvlvpc.delete_vpc,
        )
        self.get_vpc_task_status = async_to_streamed_response_wrapper(
            highlvlvpc.get_vpc_task_status,
        )
        self.list_instance_info = async_to_streamed_response_wrapper(
            highlvlvpc.list_instance_info,
        )
        self.list_vpcs = async_to_streamed_response_wrapper(
            highlvlvpc.list_vpcs,
        )
        self.retrieve_instance = async_to_streamed_response_wrapper(
            highlvlvpc.retrieve_instance,
        )
        self.retrieve_vpc = async_to_streamed_response_wrapper(
            highlvlvpc.retrieve_vpc,
        )
        self.search_instances = async_to_streamed_response_wrapper(
            highlvlvpc.search_instances,
        )
        self.search_networks = async_to_streamed_response_wrapper(
            highlvlvpc.search_networks,
        )
        self.search_ports = async_to_streamed_response_wrapper(
            highlvlvpc.search_ports,
        )
        self.search_vpcs = async_to_streamed_response_wrapper(
            highlvlvpc.search_vpcs,
        )
        self.create_image = async_to_streamed_response_wrapper(
            highlvlvpc.create_image,
        )
        self.list_image = async_to_streamed_response_wrapper(
            highlvlvpc.list_image,
        )
        self.delete_image = async_to_streamed_response_wrapper(
            highlvlvpc.delete_image
            
        )

