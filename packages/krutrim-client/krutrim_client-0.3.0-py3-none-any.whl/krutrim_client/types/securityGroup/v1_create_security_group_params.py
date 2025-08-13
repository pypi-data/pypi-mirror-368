

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from krutrim_client._utils import PropertyInfo

__all__ = ["V1CreateParams"]


class V1CreateParams(TypedDict, total=False):
    description: Required[str]
    """Description for the security group."""

    name: Required[str]
    """Name of the security group."""

    type: str
    """Type of the security group (e.g., 'lb' for load balancer)."""

    vpcid: Required[str]
    """KRN of the VPC where the security group will be created."""

    k_customer_id: Required[Annotated[str, PropertyInfo(alias="K-Customer-ID")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]
