

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcSearchNetworksParams"]


class HighlvlvpcSearchNetworksParams(TypedDict, total=False):
    vpc_id: Required[str]
    """The KRN of the VPC to search networks for."""

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]
