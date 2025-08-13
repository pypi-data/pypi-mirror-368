
from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, TypedDict

from .qos_params import QosParam
from .source_params import SourceParam

__all__ = ["VolumeCreateParams"]


class VolumeCreateParams(TypedDict, total=False):
    availability_zone: Required[str]
    """Availability zone for the volume."""

    multiattach: Required[bool]
    """Whether the volume can be attached to multiple instances."""

    name: Required[str]
    """Name of the volume."""

    size: Required[int]
    """Size of the volume in GB."""

    volumetype: str
    """Type of the volume."""

    description: Optional[str]
    """Description of the volume."""

    metadata: Dict[str, str]
    """Metadata key-value pairs for the volume."""

    qos: QosParam
    """Quality of Service (QoS) settings for the volume."""

    source: SourceParam
    """Source from which the volume is created."""
