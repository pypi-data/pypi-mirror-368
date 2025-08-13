
from typing import Optional

from ..._models import BaseModel

__all__ = ["GenericSuccessResponse"]


class GenericSuccessResponse(BaseModel):
    message: Optional[str] = None
    """A confirmation message."""

    status: Optional[str] = None
