

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcSearchPortsParams"]


class HighlvlvpcSearchPortsParams(TypedDict, total=False):
    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]

    name: str
    """Filter ports by their name."""

    network_id: str
    """Filter ports by KRN of the network."""

    page: int
    """Page number for pagination."""

    port_id: str
    """Filter ports by KRN of the port."""

    size: int
    """Number of items to return per page."""

    status: str
    """Filter ports by their status."""

    vpc_id: str
    """Filter ports by VPC KRN."""
