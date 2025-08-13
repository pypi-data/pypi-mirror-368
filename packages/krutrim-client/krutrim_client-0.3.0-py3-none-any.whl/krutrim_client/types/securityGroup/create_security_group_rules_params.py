

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from krutrim_client._utils import PropertyInfo

__all__ = ["V1CreateRuleParams"]


class V1CreateRuleParams(TypedDict, total=False):
    direction: Required[Literal["ingress", "egress"]]
    """Direction of the rule."""

    ethertypes: Required[Literal["ipv4", "ipv6"]]
    """Ethertype of the rule."""

    port_max_range: Required[Annotated[int, PropertyInfo(alias="portMaxRange")]]
    """Maximum port in the range."""

    port_min_range: Required[Annotated[int, PropertyInfo(alias="portMinRange")]]
    """Minimum port in the range."""

    protocol: Required[str]
    """Protocol for the rule (e.g., tcp, udp, icmp, or 'any')."""

    remote_ip_prefix: Required[Annotated[str, PropertyInfo(alias="remoteIPPrefix")]]
    """Remote IP CIDR prefix for the rule."""

    vpcid: Required[str]
    """KRN of the VPC associated with the rule."""

    k_customer_id: Required[Annotated[str, PropertyInfo(alias="K-Customer-ID")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]
