
from typing import Optional

from ..._models import BaseModel

__all__ = ["SuccessResponse"]


class SuccessResponse(BaseModel):
    message: Optional[str] = None

    status: Optional[str] = None

    task_id: Optional[str] = None
