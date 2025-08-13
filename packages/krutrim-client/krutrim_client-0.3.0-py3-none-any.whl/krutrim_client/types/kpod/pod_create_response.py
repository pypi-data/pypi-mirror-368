from typing import Optional

from ..._models import BaseModel

__all__ = ["PodCreateResponse"]


class PodCreateResponse(BaseModel):
    message: Optional[str] = None

    pod_id: Optional[str] = None
    """The ID of the newly created pod."""
