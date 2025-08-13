
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

from ..types.securityGroup import (
    v1_create_security_group_params,
    create_security_group_rules_params,
    attach_security_group_rules_params,
    detach_security_group_rules_params,   

)
from ..types.securityGroup.v1_create_security_group_resp import V1CreateResponse
from ..types.securityGroup.create_security_group_rules_resp import V1CreateRuleResponse
from ..types.securityGroup.attach_detach_generic_response import GenericSuccessResponse

from ..types.securityGroup.security_group_list_by_vpc_response import SecurityGroupListByVpcResponse
from ..types.securityGroup import security_group_list_by_vpc_params



__all__ = ["SecurityGroupResource", "AsyncSecurityGroupResource"]

from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)

class SecurityGroupResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SecurityGroupResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.
        """
        return SecurityGroupResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SecurityGroupResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        """
        return SecurityGroupResourceWithStreamingResponse(self)
    


    def validate_create_security_group_parameters(
    self,
    description,
    name,
    vpcid,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        if not isinstance(description, str):
            raise ValueError("'description' must be a string.")

        if not isinstance(name, str):
            raise ValueError("'name' must be a string.")

        if not isinstance(vpcid, str):
            raise ValueError("'vpcid' must be a string.")

        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")

        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")

        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")


    def validate_create_rule_parameters(
    self,
    direction,
    ethertypes,
    port_max_range,
    port_min_range,
    protocol,
    remote_ip_prefix,
    vpcid,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        if direction not in ("ingress", "egress"):
            raise ValueError("'direction' must be either 'ingress' or 'egress'.")

        if ethertypes not in ("ipv4", "ipv6"):
            raise ValueError("'ethertypes' must be either 'ipv4' or 'ipv6'.")

        if not isinstance(port_max_range, int):
            raise ValueError("'port_max_range' must be an integer.")

        if not isinstance(port_min_range, int):
            raise ValueError("'port_min_range' must be an integer.")

        if port_min_range < 0 or port_max_range < 0:
            raise ValueError("Port ranges must be non-negative integers.")

        if port_min_range > port_max_range:
            raise ValueError("'port_min_range' cannot be greater than 'port_max_range'.")

        if not isinstance(protocol, str):
            raise ValueError("'protocol' must be a string.")

        if not isinstance(remote_ip_prefix, str):
            raise ValueError("'remote_ip_prefix' must be a string.")

        if not isinstance(vpcid, str):
            raise ValueError("'vpcid' must be a string.")

        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")

        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")

        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")

    def validate_attach_rule_parameters(
    self,
    ruleid,
    securityid,
    vpcid,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        if not isinstance(ruleid, str) or not ruleid:
            raise ValueError("'ruleid' must be a non-empty string.")

        if not isinstance(securityid, str) or not securityid:
            raise ValueError("'securityid' must be a non-empty string.")

        if not isinstance(vpcid, str) or not vpcid:
            raise ValueError("'vpcid' must be a non-empty string.")

        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")

        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")

        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")
        


    def validate_detach_rule_parameters(
    self,
    ruleid: str,
    securityid: str,
    vpcid: str,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        # Validate ruleid
        if not isinstance(ruleid, str) or not ruleid.strip():
            raise ValueError("'ruleid' must be a non-empty string.")

        # Validate securityid
        if not isinstance(securityid, str) or not securityid.strip():
            raise ValueError("'securityid' must be a non-empty string.")

        # Validate vpcid
        if not isinstance(vpcid, str) or not vpcid.strip():
            raise ValueError("'vpcid' must be a non-empty string.")

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





    def create_security_group(
        self,
        *,
        description: str,
        name: str,
        vpcid: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> V1CreateResponse:
        """
        Create a new Security Group

        Args:
          description: Description for the security group.

          name: Name of the security group.

          type: Type of the security group (e.g., 'lb' for load balancer).

          vpcid: KRN of the VPC where the security group will be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_create_security_group_parameters(
        description = description,
        name = name,
        vpcid = vpcid,
        extra_headers = extra_headers,
        extra_query = extra_query,
        extra_body = extra_body,
        timeout = timeout,
        x_region = x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/securityGroup/v1",
            body=maybe_transform(
                {
                    "description": description,
                    "name": name,
                    "vpcid": vpcid,
                },
                v1_create_security_group_params.V1CreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1CreateResponse,
        ) 

    def list_by_vpc(
        self,
        vpc_krn_identifier: str,
        *,
        x_region: str,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SecurityGroupListByVpcResponse:
        """
        List security groups by VPC KRN identifier

        Args:
          limit: The maximum number of records to return (for pagination).

          offset: The number of records to skip from the beginning of the list (for pagination).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vpc_krn_identifier:
            raise ValueError(f"Expected a non-empty value for `vpc_krn_identifier` but received {vpc_krn_identifier!r}")
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._get(
            f"/securityGroup/v1/{vpc_krn_identifier}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {},
                    security_group_list_by_vpc_params.SecurityGroupListByVpcParams,
                ),
            ),
            cast_to=SecurityGroupListByVpcResponse,
        )
    

    # CREATE SECURTIY GROUP RULES
    def create_rule(
        self,
        *,
        direction: Literal["ingress", "egress"],
        ethertypes: Literal["ipv4", "ipv6"],
        port_max_range: int,
        port_min_range: int,
        protocol: str,
        remote_ip_prefix: str,
        vpcid: str,
        x_region : str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> V1CreateRuleResponse:
        """
        Create a new Security Group Rule

        Args:
          direction: Direction of the rule.

          ethertypes: Ethertype of the rule.

          port_max_range: Maximum port in the range.

          port_min_range: Minimum port in the range.

          protocol: Protocol for the rule (e.g., tcp, udp, icmp, or 'any').

          remote_ip_prefix: Remote IP CIDR prefix for the rule.

          vpcid: KRN of the VPC associated with the rule.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_create_rule_parameters(
        direction = direction,
        ethertypes = ethertypes,
        port_max_range = port_max_range,
        port_min_range = port_min_range,
        protocol = protocol,
        remote_ip_prefix = remote_ip_prefix,
        vpcid = vpcid,
        extra_headers = extra_headers,
        extra_query = extra_query,
        extra_body = extra_body,
        timeout = timeout,
        x_region = x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/securityGroup/v1/rule",
            body=maybe_transform(
                {
                    "direction": direction,
                    "ethertypes": ethertypes,
                    "port_max_range": port_max_range,
                    "port_min_range": port_min_range,
                    "protocol": protocol,
                    "remote_ip_prefix": remote_ip_prefix,
                    "vpcid": vpcid,
                },
                create_security_group_rules_params.V1CreateRuleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1CreateRuleResponse,
        )


    # ATTACH SECURITY GROUP RULE
    def attach_rule(
        self,
        *,
        ruleid: str,
        securityid: str,
        vpcid: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenericSuccessResponse:
        """
        Attach a rule to a Security Group

        Args:
          ruleid: KRN of the Security Group Rule.

          securityid: KRN of the Security Group to attach/detach the rule from.

          vpcid: KRN of the VPC associated with the Security Group and rule.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_attach_rule_parameters(
        ruleid = ruleid,
        securityid = securityid,
        vpcid = vpcid,
        extra_headers= extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
        x_region = x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/securityGroup/v1/attachrule",
            body=maybe_transform(
                {
                    "ruleid": ruleid,
                    "securityid": securityid,
                    "vpcid": vpcid,
                },
                attach_security_group_rules_params.V1AttachRuleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenericSuccessResponse,
        )

    # DETACH SECURITY GROUP RULE
    def detach_rule(
        self,
        *,
        ruleid: str,
        securityid: str,
        vpcid: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenericSuccessResponse:
        """
        Detach a rule from a Security Group

        Args:
          ruleid: KRN of the Security Group Rule.

          securityid: KRN of the Security Group to attach/detach the rule from.

          vpcid: KRN of the VPC associated with the Security Group and rule.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        self.validate_detach_rule_parameters(
                ruleid = ruleid,
                securityid = securityid,
                vpcid = vpcid,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                x_region = x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._post(
            "/securityGroup/v1/deattachrule",
            body=maybe_transform(
                {
                    "ruleid": ruleid,
                    "securityid": securityid,
                    "vpcid": vpcid,
                },
                detach_security_group_rules_params.V1DetachRuleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenericSuccessResponse,
        )
    

    def delete_security_group(
        self,
        securitygroupid: str,
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
        Delete a Security Group by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not securitygroupid:
            raise ValueError(f"Expected a non-empty value for `securitygroupid` but received {securitygroupid!r}")
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._delete(
            f"/securityGroup/v1/{securitygroupid}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )    


    def delete_rule(
        self,
        securitygroupruleid: str,
        *,
        x_region : str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a Security Group Rule by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not securitygroupruleid:
            raise ValueError(
                f"Expected a non-empty value for `securitygroupruleid` but received {securitygroupruleid!r}"
            )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return self._delete(
            f"/securityGroup/v1/rule/{securitygroupruleid}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )






class AsyncSecurityGroupResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSecurityGroupResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.
        """
        return AsyncSecurityGroupResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSecurityGroupResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.
        """
        return AsyncSecurityGroupResourceWithStreamingResponse(self)
    

    async def validate_create_security_group_parameters(
    self,
    description,
    name,
    vpcid,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        if not isinstance(description, str):
            raise ValueError("'description' must be a string.")

        if not isinstance(name, str):
            raise ValueError("'name' must be a string.")

        if not isinstance(vpcid, str):
            raise ValueError("'vpcid' must be a string.")

        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")

        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")

        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")


    async def validate_create_rule_parameters(
    self,
    direction,
    ethertypes,
    port_max_range,
    port_min_range,
    protocol,
    remote_ip_prefix,
    vpcid,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        if direction not in ("ingress", "egress"):
            raise ValueError("'direction' must be either 'ingress' or 'egress'.")

        if ethertypes not in ("ipv4", "ipv6"):
            raise ValueError("'ethertypes' must be either 'ipv4' or 'ipv6'.")

        if not isinstance(port_max_range, int):
            raise ValueError("'port_max_range' must be an integer.")

        if not isinstance(port_min_range, int):
            raise ValueError("'port_min_range' must be an integer.")

        if port_min_range < 0 or port_max_range < 0:
            raise ValueError("Port ranges must be non-negative integers.")

        if port_min_range > port_max_range:
            raise ValueError("'port_min_range' cannot be greater than 'port_max_range'.")

        if not isinstance(protocol, str):
            raise ValueError("'protocol' must be a string.")

        if not isinstance(remote_ip_prefix, str):
            raise ValueError("'remote_ip_prefix' must be a string.")

        if not isinstance(vpcid, str):
            raise ValueError("'vpcid' must be a string.")

        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")

        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")

        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")

    async def validate_attach_rule_parameters(
    self,
    ruleid,
    securityid,
    vpcid,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        if not isinstance(ruleid, str) or not ruleid:
            raise ValueError("'ruleid' must be a non-empty string.")

        if not isinstance(securityid, str) or not securityid:
            raise ValueError("'securityid' must be a non-empty string.")

        if not isinstance(vpcid, str) or not vpcid:
            raise ValueError("'vpcid' must be a non-empty string.")

        if extra_headers is not None and not isinstance(extra_headers, dict):
            raise ValueError("'extra_headers' must be a dictionary if provided.")

        if extra_query is not None and not isinstance(extra_query, dict):
            raise ValueError("'extra_query' must be a dictionary if provided.")

        if extra_body is not None and not isinstance(extra_body, dict):
            raise ValueError("'extra_body' must be a dictionary if provided.")

        if timeout not in (None, NOT_GIVEN) and not isinstance(timeout, (int, float, httpx.Timeout)):
            raise ValueError("'timeout' must be a float, int, or httpx.Timeout if provided.")

        if x_region not in ("In-Bangalore-1", "In-Hyderabad-1"):
            raise ValueError("'x_region' must be either 'In-Bangalore-1' or 'In-Hyderabad-1'.")
        


    async def validate_detach_rule_parameters(
    self,
    ruleid: str,
    securityid: str,
    vpcid: str,
    x_region,
    extra_headers=None,
    extra_query=None,
    extra_body=None,
    timeout=None
    ):
        # Validate ruleid
        if not isinstance(ruleid, str) or not ruleid.strip():
            raise ValueError("'ruleid' must be a non-empty string.")

        # Validate securityid
        if not isinstance(securityid, str) or not securityid.strip():
            raise ValueError("'securityid' must be a non-empty string.")

        # Validate vpcid
        if not isinstance(vpcid, str) or not vpcid.strip():
            raise ValueError("'vpcid' must be a non-empty string.")

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


    

    async def create_security_group(
        self,
        *,
        description: str,
        name: str,
        vpcid: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> V1CreateResponse:
        """
        Create a new Security Group

        Args:
          description: Description for the security group.

          name: Name of the security group.

          type: Type of the security group (e.g., 'lb' for load balancer).

          vpcid: KRN of the VPC where the security group will be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_create_security_group_parameters(
            description = description,
            name = name,
            vpcid = vpcid,
            extra_headers = extra_headers,
            extra_query = extra_query,
            extra_body = extra_body,
            timeout = timeout,
            x_region = x_region
            )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/securityGroup/v1",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "name": name,
                    "vpcid": vpcid,
                },
                v1_create_security_group_params.V1CreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1CreateResponse,
        )

    async def list_by_vpc(
        self,
        vpc_krn_identifier: str,
        *,
        x_region: str,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SecurityGroupListByVpcResponse:
        """
        List security groups by VPC KRN identifier

        Args:
          limit: The maximum number of records to return (for pagination).

          offset: The number of records to skip from the beginning of the list (for pagination).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vpc_krn_identifier:
            raise ValueError(f"Expected a non-empty value for `vpc_krn_identifier` but received {vpc_krn_identifier!r}")
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._get(
            f"/securityGroup/v1/{vpc_krn_identifier}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {},
                    security_group_list_by_vpc_params.SecurityGroupListByVpcParams,
                ),
            ),
            cast_to=SecurityGroupListByVpcResponse,
        )


    async def create_rule(
        self,
        *,
        direction: Literal["ingress", "egress"],
        ethertypes: Literal["ipv4", "ipv6"],
        port_max_range: int,
        port_min_range: int,
        protocol: str,
        remote_ip_prefix: str,
        vpcid: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> V1CreateRuleResponse:
        """
        Create a new Security Group Rule

        Args:
          direction: Direction of the rule.

          ethertypes: Ethertype of the rule.

          port_max_range: Maximum port in the range.

          port_min_range: Minimum port in the range.

          protocol: Protocol for the rule (e.g., tcp, udp, icmp, or 'any').

          remote_ip_prefix: Remote IP CIDR prefix for the rule.

          vpcid: KRN of the VPC associated with the rule.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """

        await self.validate_create_rule_parameters(
            direction = direction,
            ethertypes = ethertypes,
            port_max_range = port_max_range,
            port_min_range = port_min_range,
            protocol = protocol,
            remote_ip_prefix = remote_ip_prefix,
            vpcid = vpcid,
            extra_headers = extra_headers,
            extra_query = extra_query,
            extra_body = extra_body,
            timeout = timeout,
            x_region = x_region
            )

        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/securityGroup/v1/rule",
            body=await async_maybe_transform(
                {
                    "direction": direction,
                    "ethertypes": ethertypes,
                    "port_max_range": port_max_range,
                    "port_min_range": port_min_range,
                    "protocol": protocol,
                    "remote_ip_prefix": remote_ip_prefix,
                    "vpcid": vpcid,
                },
                create_security_group_rules_params.V1CreateRuleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1CreateRuleResponse,
        )


    async def attach_rule(
        self,
        *,
        ruleid: str,
        securityid: str,
        vpcid: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenericSuccessResponse:
        """
        Attach a rule to a Security Group

        Args:
          ruleid: KRN of the Security Group Rule.

          securityid: KRN of the Security Group to attach/detach the rule from.

          vpcid: KRN of the VPC associated with the Security Group and rule.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_attach_rule_parameters(
        ruleid = ruleid,
        securityid = securityid,
        vpcid = vpcid,
        extra_headers= extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
        x_region= x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/securityGroup/v1/attachrule",
            body= await async_maybe_transform(
                {
                    "ruleid": ruleid,
                    "securityid": securityid,
                    "vpcid": vpcid,
                },
                attach_security_group_rules_params.V1AttachRuleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenericSuccessResponse,
        )


    async def detach_rule(
        self,
        *,
        ruleid: str,
        securityid: str,
        vpcid: str,
        x_region: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenericSuccessResponse:
        """
        Detach a rule from a Security Group

        Args:
          ruleid: KRN of the Security Group Rule.

          securityid: KRN of the Security Group to attach/detach the rule from.

          vpcid: KRN of the VPC associated with the Security Group and rule.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        await self.validate_detach_rule_parameters(
                ruleid = ruleid,
                securityid = securityid,
                vpcid = vpcid,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                x_region = x_region
        )
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._post(
            "/securityGroup/v1/deattachrule",
            body=await async_maybe_transform(
                {
                    "ruleid": ruleid,
                    "securityid": securityid,
                    "vpcid": vpcid,
                },
                detach_security_group_rules_params.V1DetachRuleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenericSuccessResponse,
        )

    async def delete_security_group(
        self,
        securitygroupid: str,
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
        Delete a Security Group by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not securitygroupid:
            raise ValueError(f"Expected a non-empty value for `securitygroupid` but received {securitygroupid!r}")
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._delete(
            f"/securityGroup/v1/{securitygroupid}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def delete_rule(
        self,
        securitygroupruleid: str,
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
        Delete a Security Group Rule by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not securitygroupruleid:
            raise ValueError(
                f"Expected a non-empty value for `securitygroupruleid` but received {securitygroupruleid!r}"
            )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {"x-region": x_region, **(extra_headers or {})}
        return await self._delete(
            f"/securityGroup/v1/rule/{securitygroupruleid}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class SecurityGroupResourceWithRawResponse:
    def __init__(self, securityGroup: SecurityGroupResource) -> None:
        self._securityGroup = securityGroup

        self.delete_security_group = to_raw_response_wrapper(
            securityGroup.delete_security_group,
        )
        
        self.create_security_group = to_raw_response_wrapper(
            securityGroup.create_security_group,
        )

        self.create_rule = to_raw_response_wrapper(
            securityGroup.create_rule,
        )

        self.attach_rule = to_raw_response_wrapper(
            securityGroup.attach_rule,
        )

        self.detach_rule = to_raw_response_wrapper(
            securityGroup.detach_rule,
        )

        self.list_by_vpc = to_raw_response_wrapper(
            securityGroup.list_by_vpc,
        )
        self.delete_rule = to_raw_response_wrapper(
            securityGroup.delete_rule,
        )
        




class AsyncSecurityGroupResourceWithRawResponse:
    def __init__(self, securityGroup: AsyncSecurityGroupResource) -> None:
        self._securityGroup = securityGroup

        self.delete_security_group = async_to_raw_response_wrapper(
            securityGroup.delete_security_group,
        )

        self.create_security_group = async_to_raw_response_wrapper(
            securityGroup.create_security_group,
        )

        self.create_rule = async_to_raw_response_wrapper(
            securityGroup.create_rule,
        )

        self.attach_rule = async_to_raw_response_wrapper(
            securityGroup.attach_rule,
        )

        self.detach_rule = async_to_raw_response_wrapper(
            securityGroup.detach_rule,
        )

        self.list_by_vpc = async_to_raw_response_wrapper(
            securityGroup.list_by_vpc,
        )
        self.delete_rule = async_to_raw_response_wrapper(
            securityGroup.delete_rule,
        )
        


class SecurityGroupResourceWithStreamingResponse:
    def __init__(self, securityGroup: SecurityGroupResource) -> None:
        self._securityGroup = securityGroup

        self.delete_security_group = to_streamed_response_wrapper(
            securityGroup.delete_security_group,
        )

        self.create_security_group = to_streamed_response_wrapper(
            securityGroup.create_security_group,
        )

        self.create_rule = to_streamed_response_wrapper(
            securityGroup.create_rule,
        )

        self.attach_rule = to_streamed_response_wrapper(
            securityGroup.attach_rule,
        )

        self.detach_rule = to_streamed_response_wrapper(
            securityGroup.detach_rule,
        )

        self.list_by_vpc = to_streamed_response_wrapper(
            securityGroup.list_by_vpc,
        )
        self.delete_rule = to_streamed_response_wrapper(
            securityGroup.delete_rule,
        )


class AsyncSecurityGroupResourceWithStreamingResponse:
    def __init__(self, securityGroup: AsyncSecurityGroupResource) -> None:
        self._securityGroup = securityGroup

        self.delete_security_group = async_to_streamed_response_wrapper(
            securityGroup.delete_security_group,
        )

        self.create_security_group = async_to_streamed_response_wrapper(
            securityGroup.create_security_group,
        )
        
        self.create_rule = async_to_streamed_response_wrapper(
            securityGroup.create_rule,
        )

        self.attach_rule = async_to_streamed_response_wrapper(
            securityGroup.attach_rule,
        )

        self.detach_rule = async_to_streamed_response_wrapper(
            securityGroup.detach_rule,
        )
        self.list_by_vpc = async_to_streamed_response_wrapper(
            securityGroup.list_by_vpc,
        )
        self.delete_rule = async_to_streamed_response_wrapper(
            securityGroup.delete_rule,
        )

        

    

    