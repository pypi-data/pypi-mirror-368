# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["V1PerformActionResponse"]


class V1PerformActionResponse(BaseModel):
    instance_krn: Optional[str] = None
    """The KRN of the instance on which the action was performed."""

    message: Optional[str] = None
    """A confirmation message."""

    status: Optional[str] = None
    """The current status of the instance or action."""

    task_id: Optional[str] = None
    """Optional task ID for tracking asynchronous operations."""
