# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from krutrim_client._models import BaseModel

__all__ = ["SecurityGroupListByVpcResponse", "Item", "ItemRule"]


class ItemRule(BaseModel):
    direction: Optional[Literal["ingress", "egress"]] = None
    """The direction of the traffic (inbound or outbound)."""

    port_range_max: Optional[int] = FieldInfo(alias="portRangeMax", default=None)
    """The maximum port number in the range (inclusive)."""

    port_range_min: Optional[int] = FieldInfo(alias="portRangeMin", default=None)
    """The minimum port number in the range (inclusive)."""

    protocol: Optional[str] = None
    """The IP protocol name (e.g., "tcp", "udp", "icmp") or "any"."""

    remote: Optional[str] = None
    """
    The source (for ingress) or destination (for egress) CIDR IP range or another
    security group ID.
    """


class Item(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the security group."""

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)
    """The timestamp when the security group was created."""

    description: Optional[str] = None
    """A brief description of the security group's purpose."""

    name: Optional[str] = None
    """The name of the security group."""

    rules: Optional[List[ItemRule]] = None
    """A list of ingress and egress rules for the security group."""

    vpc_id: Optional[str] = FieldInfo(alias="vpcId", default=None)
    """The UUID of the VPC this security group belongs to."""


class SecurityGroupListByVpcResponse(BaseModel):
    items: Optional[List[Item]] = None
    """An array of security group objects."""

    limit: Optional[int] = None
    """The maximum number of records requested."""

    offset: Optional[int] = None
    """The number of records skipped."""

    total_count: Optional[int] = FieldInfo(alias="totalCount", default=None)
    """The total number of security groups matching the criteria."""
