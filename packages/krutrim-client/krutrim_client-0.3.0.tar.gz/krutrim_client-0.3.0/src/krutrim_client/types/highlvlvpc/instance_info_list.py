
from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .instance_info import InstanceInfo

__all__ = ["InstanceInfoList"]


class InstanceInfoList(BaseModel):
    instances: Optional[List[InstanceInfo]] = None

    page: Optional[int] = None
    """The current page number."""

    page_size: Optional[int] = FieldInfo(alias="pageSize", default=None)
    """The number of items per page."""

    total_count: Optional[int] = FieldInfo(alias="totalCount", default=None)
    """The total number of instances matching the filter."""

    total_pages: Optional[int] = FieldInfo(alias="totalPages", default=None)
    """The total number of pages."""
