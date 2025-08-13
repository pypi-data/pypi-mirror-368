
from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcRetrieveVpcParams"]


class HighlvlvpcRetrieveVpcParams(TypedDict, total=False):
    k_customer_id: Required[Annotated[str, PropertyInfo(alias="k-customer-id")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]

    vpc_id: Optional[str]
    """The KRN of the VPC to retrieve."""

    vpc_name: Optional[str]
    """The name of the VPC to retrieve."""
