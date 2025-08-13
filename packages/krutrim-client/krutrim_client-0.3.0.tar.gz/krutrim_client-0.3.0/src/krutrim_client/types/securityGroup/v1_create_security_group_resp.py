from typing import Optional

from ..._models import BaseModel

__all__ = ["V1CreateResponse"]


class V1CreateResponse(BaseModel):
    id: Optional[str] = None
    """The KRN of the newly created Security Group."""

    message: Optional[str] = None
    """A confirmation message."""

    name: Optional[str] = None
    """The name of the created Security Group."""

    status: Optional[str] = None
    """The status of the Security Group."""
