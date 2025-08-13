# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["SshkeyCreateResponse"]


class SshkeyCreateResponse(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the SSH key."""

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)
    """The timestamp when the SSH key was created."""

    fingerprint: Optional[str] = None
    """The SHA256 fingerprint of the public key."""

    key_name: Optional[str] = FieldInfo(alias="keyName", default=None)
    """The name of the SSH key."""

    public_key: Optional[str] = FieldInfo(alias="publicKey", default=None)
    """The public SSH key string."""
