#

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["HighlvlvpcSearchVpcsParams"]


class HighlvlvpcSearchVpcsParams(TypedDict, total=False):
    name: str
    """Filter VPCs by name."""

    page: int
    """Page number for pagination."""

    size: int
    """Number of items to return per page."""

    status: str
    """Filter VPCs by status."""
