
from typing import List, Optional

from ..._models import BaseModel
class HighlvlvpcListImageResponse(BaseModel):
    images: List[dict]
    """List of images returned from the search."""