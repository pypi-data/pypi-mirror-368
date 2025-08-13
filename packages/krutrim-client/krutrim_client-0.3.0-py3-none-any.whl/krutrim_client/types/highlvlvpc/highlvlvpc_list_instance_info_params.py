

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcListInstanceInfoParams"]


class HighlvlvpcListInstanceInfoParams(TypedDict, total=False):
    k_customer_id: Required[Annotated[str, PropertyInfo(alias="k-customer-id")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]

    page: int
    """Page number for pagination."""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """Number of instances per page."""

    vpc_id: str
    """KRN of the VPC to filter instances."""
