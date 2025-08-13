# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from krutrim_client._models import BaseModel

__all__ = ["SshkeyRetrieveResponse"]


class SshkeyRetrieveResponse(BaseModel):

    key_name: Optional[str] = FieldInfo(alias="keyName", default=None)
    """The user-defined name of the SSH key."""


