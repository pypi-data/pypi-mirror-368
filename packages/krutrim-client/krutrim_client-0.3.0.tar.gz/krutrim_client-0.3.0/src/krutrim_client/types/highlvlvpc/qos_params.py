

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["QosParam", "Bandwidth", "Iops"]


class Bandwidth(TypedDict, total=False):
    read_bytes_sec: Required[int]
    """Read bandwidth in bytes per second."""

    write_bytes_sec: Required[int]
    """Write bandwidth in bytes per second."""


class Iops(TypedDict, total=False):
    read_iops_sec: Required[int]
    """Read IOPS per second."""

    write_iops_sec: Required[int]
    """Write IOPS per second."""


class QosParam(TypedDict, total=False):
    bandwidth: Bandwidth
    """Bandwidth settings for QoS."""

    iops: Iops
    """IOPS settings for QoS."""
