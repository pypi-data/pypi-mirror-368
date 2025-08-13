from __future__ import annotations
from typing_extensions import Required, TypedDict
from ..._models import BaseModel

__all__ = ["HighlvlvpcCreateImageResponse"]

class HighlvlvpcCreateImageResponse(BaseModel):
    image: Required[str]
    """The image ID or URL returned by the API"""
