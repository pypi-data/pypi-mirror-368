from __future__ import annotations
from typing_extensions import Required, Annotated, TypedDict
from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcDeleteImageParams"]

class HighlvlvpcDeleteImageParams(TypedDict, total=False):
    snapshot_krn: Required[str]
    """The KRN of the image to delete."""

