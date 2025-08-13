
from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcCreateSubnetParams", "SubnetData"]


class HighlvlvpcCreateSubnetParams(TypedDict, total=False):
    subnet_data: Required[SubnetData]

    vpc_id: Required[str]
    """The ID of the VPC where the subnet will be created."""

    k_customer_id: Required[Annotated[str, PropertyInfo(alias="k-customer-id")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]


class SubnetData(TypedDict, total=False):
    cidr: Required[str]

    ip_version: Required[Literal[4, 6]]

    name: Required[str]

    description: Optional[str]

    gateway_ip: Optional[str]
