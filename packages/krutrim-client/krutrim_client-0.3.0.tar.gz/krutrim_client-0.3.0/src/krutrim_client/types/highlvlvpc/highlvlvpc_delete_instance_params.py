
from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcDeleteInstanceParams"]


class HighlvlvpcDeleteInstanceParams(TypedDict, total=False):
    k_customer_id: Required[Annotated[str, PropertyInfo(alias="k-customer-id")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]

    instance_krn: Annotated[Optional[str], PropertyInfo(alias="instanceKrn")]
    """The KRN of the instance to be deleted."""

    instance_name: Annotated[Optional[str], PropertyInfo(alias="instanceName")]
    """The name of the instance to be deleted."""
