
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["Source"]


class Source(BaseModel):
    id: str
    """KRN or ID of the source (image, volume, or snapshot)."""

    type: Literal["image", "volume", "snapshot"]
    """Type of source."""
