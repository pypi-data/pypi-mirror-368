
from typing import Optional

from ..._models import BaseModel

__all__ = ["Qos", "Bandwidth", "Iops"]


class Bandwidth(BaseModel):
    read_bytes_sec: int
    """Read bandwidth in bytes per second."""

    write_bytes_sec: int
    """Write bandwidth in bytes per second."""


class Iops(BaseModel):
    read_iops_sec: int
    """Read IOPS per second."""

    write_iops_sec: int
    """Write IOPS per second."""


class Qos(BaseModel):
    bandwidth: Optional[Bandwidth] = None
    """Bandwidth settings for QoS."""

    iops: Optional[Iops] = None
    """IOPS settings for QoS."""
