

from typing import List, Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["PortDetail", "FixedIP"]


class FixedIP(BaseModel):
    ip_address: Optional[str] = None

    subnet_id: Optional[str] = None


class PortDetail(BaseModel):
    admin_state_up: Optional[bool] = None
    """Administrative state of the port."""

    created_at: Optional[datetime] = None
    """Timestamp of port creation."""

    device_id: Optional[str] = None
    """ID of the device that uses this port (e.g., VM ID)."""

    device_owner: Optional[str] = None
    """Entity that owns the port (e.g., network:dhcp, compute:nova)."""

    fixed_ips: Optional[List[FixedIP]] = None
    """List of fixed IP addresses assigned to the port."""

    floating_ip_address: Optional[str] = None
    """The floating IP address associated with the port, if any."""

    mac_address: Optional[str] = None
    """MAC address of the port."""

    name: Optional[str] = None
    """Name of the port."""

    network_id: Optional[str] = None
    """KRN of the network this port belongs to."""

    port_id: Optional[str] = None
    """The unique identifier or KRN of the created port."""

    security_group_krns: Optional[List[str]] = None
    """List of security group KRNs attached to this port."""

    status: Optional[str] = None
    """Current status of the port (e.g., ACTIVE, DOWN, BUILD)."""

    subnet_id: Optional[str] = None
    """KRN of the subnet this port is associated with."""

    updated_at: Optional[datetime] = None
    """Timestamp of last port update."""
