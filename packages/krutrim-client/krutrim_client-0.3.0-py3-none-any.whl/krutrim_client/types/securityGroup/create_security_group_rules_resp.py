

from typing import Optional

from ..._models import BaseModel

__all__ = ["V1CreateRuleResponse"]


class V1CreateRuleResponse(BaseModel):
    id: Optional[str] = None
    """The UUID of the newly created Security Group Rule."""

    message: Optional[str] = None
    """A confirmation message."""

    status: Optional[str] = None
    """The status of the rule (e.g., 'active', 'creating')."""
