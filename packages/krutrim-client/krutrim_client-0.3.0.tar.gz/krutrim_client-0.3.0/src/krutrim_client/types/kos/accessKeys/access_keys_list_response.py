from typing import List, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from krutrim_client._models import BaseModel


__all__ = ["AccessKeyListResponse", "AccessKeyListResponseItem"]


class AccessKeyListResponseItem(BaseModel):
    access_key_id: Optional[str] = FieldInfo(alias="access_key_id", default=None)
    """The ID of the access key."""

    created_at: Optional[datetime] = None
    """Timestamp when the access key was created."""

    key_name: Optional[str] = None
    """The name given to the access key."""

    status: Optional[str] = None
    """The status of the access key (e.g., Active, Inactive)."""


AccessKeyListResponse: TypeAlias = List[AccessKeyListResponseItem]
