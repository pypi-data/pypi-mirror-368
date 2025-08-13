

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcGetVpcTaskStatusParams"]


class HighlvlvpcGetVpcTaskStatusParams(TypedDict, total=False):
    task_id: Required[str]
    """The task ID of the VPC operation"""

    k_customer_id: Required[Annotated[str, PropertyInfo(alias="k-customer-id")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]
