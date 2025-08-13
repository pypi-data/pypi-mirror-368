

from typing import Dict, List, Optional
from datetime import datetime

from .qos import Qos
from .source import Source
from ..._models import BaseModel

__all__ = ["VolumeDetail", "Attachment"]


class Attachment(BaseModel):
    device: Optional[str] = None

    instance_id: Optional[str] = None


class VolumeDetail(BaseModel):
    id: Optional[str] = None
    """Unique identifier (UUID) of the volume."""

    attachments: Optional[List[Attachment]] = None
    """List of instances to which the volume is attached."""

    availability_zone: Optional[str] = None
    """Availability zone of the volume."""

    created_at: Optional[datetime] = None
    """Timestamp of volume creation."""

    krn: Optional[str] = None
    """Krutrim Resource Name (KRN) of the volume."""

    metadata: Optional[Dict[str, str]] = None
    """Metadata key-value pairs for the volume."""

    multiattach: Optional[bool] = None
    """Whether the volume can be attached to multiple instances."""

    name: Optional[str] = None
    """Name of the volume."""

    qos: Optional[Qos] = None
    """Quality of Service (QoS) settings for the volume."""

    size: Optional[int] = None
    """Size of the volume in GB."""

    source: Optional[Source] = None
    """Source from which the volume is created."""

    status: Optional[str] = None
    """Current status of the volume."""

    updated_at: Optional[datetime] = None
    """Timestamp of last volume update."""

    volumetype: Optional[str] = None
    """Type of the volume."""
