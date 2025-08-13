

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcDeleteVpcParams"]


class HighlvlvpcDeleteVpcParams(TypedDict, total=False):
    vpc_id: Required[str]
    """The ID of the VPC to delete."""

    k_customer_id: Required[Annotated[str, PropertyInfo(alias="k-customer-id")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]
