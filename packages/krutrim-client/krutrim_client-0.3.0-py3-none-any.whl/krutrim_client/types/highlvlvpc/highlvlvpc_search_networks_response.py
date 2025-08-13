
from typing import List, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from ..._models import BaseModel

__all__ = ["HighlvlvpcSearchNetworksResponse", "HighlvlvpcSearchNetworksResponseItem"]


class HighlvlvpcSearchNetworksResponseItem(BaseModel):
    admin_state_up: Optional[bool] = None
    """The administrative state of the network (true for up, false for down)."""

    created_at: Optional[datetime] = None
    """Timestamp of when the network was created."""

    name: Optional[str] = None
    """Name of the network."""

    network_id: Optional[str] = None
    """The unique KRN of the network."""

    shared: Optional[bool] = None
    """Indicates whether this network is shared across projects."""

    status: Optional[str] = None
    """The status of the network (e.g., ACTIVE, DOWN, BUILD, ERROR)."""

    subnets: Optional[List[str]] = None
    """List of KRNs of subnets attached to this network."""

    updated_at: Optional[datetime] = None
    """Timestamp of when the network was last updated."""

    vpc_id: Optional[str] = None
    """KRN of the VPC this network belongs to."""


HighlvlvpcSearchNetworksResponse: TypeAlias = List[HighlvlvpcSearchNetworksResponseItem]
