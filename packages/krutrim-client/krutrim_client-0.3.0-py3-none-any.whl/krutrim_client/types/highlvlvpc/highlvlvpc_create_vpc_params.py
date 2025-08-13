
from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcCreateVpcParams", "Network", "SecurityGroup", "SecurityGroupRule", "Subnet", "Vpc"]


class HighlvlvpcCreateVpcParams(TypedDict, total=False):
    k_customer_id: Required[Annotated[str, PropertyInfo(alias="k-customer-id")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]

    network: Network

    security_group: SecurityGroup

    security_group_rule: SecurityGroupRule

    subnet: Subnet

    vpc: Vpc


class Network(TypedDict, total=False):
    admin_state_up: bool
    """Administrative state of the network."""

    name: str
    """Name of the network to be created within the VPC."""


class SecurityGroup(TypedDict, total=False):
    description: str
    """Description for the security group."""

    name: str
    """Name of the default security group to be created."""


class SecurityGroupRule(TypedDict, total=False):
    direction: Literal["ingress", "egress"]
    """Direction of the rule."""

    ethertypes: Literal["IPv4", "IPv6"]
    """Ethertype of the rule."""

    port_max_range: Annotated[int, PropertyInfo(alias="portMaxRange")]
    """Maximum port range."""

    port_min_range: Annotated[int, PropertyInfo(alias="portMinRange")]
    """Minimum port range."""

    protocol: str
    """Protocol for the rule (e.g., tcp, udp, icmp)."""

    remote_ip_prefix: Annotated[str, PropertyInfo(alias="remoteIPPrefix")]
    """Remote IP prefix for the rule."""


class Subnet(TypedDict, total=False):
    cidr: Required[str]
    """CIDR block for the subnet."""

    description: Required[str]
    """Description for the subnet."""

    gateway_ip: Required[str]
    """Gateway IP for the subnet."""

    ip_version: Required[Literal[4, 6]]
    """IP version for the subnet (4 or 6)."""

    name: Required[str]
    """Name of the subnet."""

    egress: Optional[bool]
    """Default egress policy (semantics depend on implementation)."""

    ingress: Optional[bool]
    """Default ingress policy (semantics depend on implementation)."""


class Vpc(TypedDict, total=False):
    description: Required[str]
    """Description for the VPC."""

    enabled: Required[bool]
    """Whether the VPC is enabled."""

    name: Required[str]
    """Name of the VPC."""
