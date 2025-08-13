
from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcSearchInstancesParams"]


class HighlvlvpcSearchInstancesParams(TypedDict, total=False):
    vpc_id: Required[str]
    """The KRN of the VPC to filter instances."""

    k_customer_id: Required[Annotated[str, PropertyInfo(alias="k-customer-id")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]

    x_user_email: Required[Annotated[str, PropertyInfo(alias="x-user-email")]]

    limit: int
    """Maximum number of instances to return per page."""

    page: int
    """Page number for pagination."""

    ip_fixed: Optional[str]
    """Filter instances by fixed IP address."""

    ip_floating: Optional[str]
    """Filter instances by floating IP address."""

    krn: Optional[str]
    """Filter instances by their KRN."""

    name: Optional[str]
    """Filter instances by name (exact match or contains, depending on API)."""
