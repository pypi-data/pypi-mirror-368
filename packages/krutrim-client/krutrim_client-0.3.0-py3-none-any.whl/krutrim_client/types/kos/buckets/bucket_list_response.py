from typing import List, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from krutrim_client._models import BaseModel


__all__ = ["BucketListResponse", "BucketListResponseItem"]


class BucketListResponseItem(BaseModel):
    anonymous_access: Optional[bool] = None
    """Whether anonymous access is allowed."""

    created_at: Optional[datetime] = None
    """Timestamp when the bucket was created."""

    description: Optional[str] = None
    """Description of the bucket."""

    name: Optional[str] = None
    """The name of the bucket."""

    region: Optional[str] = None
    """The region where the bucket is located."""

    versioning: Optional[bool] = None
    """Whether versioning is enabled."""


BucketListResponse: TypeAlias = List[BucketListResponseItem]
