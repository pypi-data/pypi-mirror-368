

from typing import List, Optional

from ..._models import BaseModel
from .vpc_detail import VpcDetail

__all__ = ["HighlvlvpcSearchVpcsResponse"]


class HighlvlvpcSearchVpcsResponse(BaseModel):
    page: Optional[int] = None
    """The current page number."""

    size: Optional[int] = None
    """The number of items per page."""

    total_count: Optional[int] = None
    """The total number of VPCs matching the filter."""

    total_pages: Optional[int] = None
    """The total number of pages."""

    vpcs: Optional[List[VpcDetail]] = None
