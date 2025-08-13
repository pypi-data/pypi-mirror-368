from typing import Optional

from pydantic import Field as FieldInfo


from krutrim_client._models import BaseModel

__all__ = ["AccessKeyCreateResponse"]


class AccessKeyCreateResponse(BaseModel):
    access_key: Optional[str] = FieldInfo(alias="access_key", default=None)
    """The generated access key ID."""

    message: Optional[str] = None

    secret_key: Optional[str] = FieldInfo(alias="secret_key", default=None)
    """The generated secret access key."""
