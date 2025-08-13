from typing import Optional

from ..._models import BaseModel

__all__ = ["PodDeleteResponse"]


class PodDeleteResponse(BaseModel):
    message: Optional[str] = None
