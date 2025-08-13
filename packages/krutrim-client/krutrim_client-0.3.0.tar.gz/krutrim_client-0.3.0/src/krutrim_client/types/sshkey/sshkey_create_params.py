# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["SshkeyCreateParams"]


class SshkeyCreateParams(TypedDict, total=False):
    key_name: Required[Annotated[str, PropertyInfo(alias="keyName")]]
    """The name for the SSH key. Must be unique."""

    public_key: Required[Annotated[str, PropertyInfo(alias="publicKey")]]
    """The actual public SSH key string (e.g., starting with "ssh-rsa")."""
