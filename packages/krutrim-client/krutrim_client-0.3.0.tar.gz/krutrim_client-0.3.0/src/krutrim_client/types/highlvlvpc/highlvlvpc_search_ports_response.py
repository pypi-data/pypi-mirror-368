

from typing import List, Optional

from ..._models import BaseModel
from .port_detail import PortDetail

__all__ = ["HighlvlvpcSearchPortsResponse"]


class HighlvlvpcSearchPortsResponse(BaseModel):
    page: Optional[int] = None
    """The current page number."""

    ports: Optional[List[PortDetail]] = None

    size: Optional[int] = None
    """The number of items per page."""

    total_count: Optional[int] = None
    """The total number of ports matching the filter."""

    total_pages: Optional[int] = None
    """The total number of pages."""
