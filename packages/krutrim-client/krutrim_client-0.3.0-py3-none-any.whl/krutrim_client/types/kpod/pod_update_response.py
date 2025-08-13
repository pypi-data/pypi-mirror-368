from typing import Optional

from ..._models import BaseModel

__all__ = ["PodUpdateResponse"]


class PodUpdateResponse(BaseModel):
    message: Optional[str] = None

    status: Optional[str] = None
