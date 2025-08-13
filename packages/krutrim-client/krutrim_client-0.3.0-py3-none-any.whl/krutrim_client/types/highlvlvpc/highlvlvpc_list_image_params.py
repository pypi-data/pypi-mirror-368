from __future__ import annotations
from typing_extensions import Required, Annotated, TypedDict
from ..._utils import PropertyInfo  

__all__ = ["HighlvlvpcListImageParams"]

class HighlvlvpcListImageParams(TypedDict, total=False):
    region_id: Required[str]
    """The region ID to filter images by."""
    
    limit: Annotated[int, PropertyInfo(alias="limit")]
    """Optional: Maximum number of images to return per page."""
    
    page: Annotated[int, PropertyInfo(alias="page")]
    """Optional: Page number for pagination."""
    