

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["VpcDetail"]


class VpcDetail(BaseModel):
    cidr_block: Optional[str] = None
    """The primary IPv4 CIDR block for the VPC."""

    created_at: Optional[datetime] = None
    """Timestamp of when the VPC was created."""

    description: Optional[str] = None
    """Description of the VPC."""

    enabled: Optional[bool] = None
    """Indicates whether the VPC is enabled."""

    name: Optional[str] = None
    """Name of the VPC."""

    status: Optional[str] = None
    """Current status of the VPC."""

    updated_at: Optional[datetime] = None
    """Timestamp of when the VPC was last updated."""

    vpc_id: Optional[str] = None
    """The unique Krutrim Resource Name (KRN) of the VPC."""
