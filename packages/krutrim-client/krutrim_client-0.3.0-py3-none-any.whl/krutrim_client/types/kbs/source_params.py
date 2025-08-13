

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["SourceParam"]


class SourceParam(TypedDict, total=False):
    id: Required[str]
    """KRN or ID of the source (image, volume, or snapshot)."""

    type: Required[Literal["image", "volume", "snapshot"]]
    """Type of source."""
