from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcCreateImageParams"]

class HighlvlvpcCreateImageParams(TypedDict, total=False):
    name: Required[str]
    """The name for the image to be created."""

    instance_krn: Required[str]
    """The KRN of the instance to create the image from."""

    description: Annotated[str, PropertyInfo(alias="description")]
    """Optional description for the image."""
