

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcRetrieveInstanceParams"]


class HighlvlvpcRetrieveInstanceParams(TypedDict, total=False):
    krn: Required[str]
    """The KRN of the instance to retrieve."""

    k_customer_id: Required[Annotated[str, PropertyInfo(alias="k-customer-id")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]
