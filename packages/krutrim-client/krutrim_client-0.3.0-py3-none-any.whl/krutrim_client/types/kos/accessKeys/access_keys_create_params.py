from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from krutrim_client._utils import PropertyInfo




__all__ = ["AccessKeyCreateParams"]


class AccessKeyCreateParams(TypedDict, total=False):
    key_name: Required[str]
    """The name for the access key."""

    region: Required[str]
    """The region associated with the access key."""

    x_region_id: Required[Annotated[str, PropertyInfo(alias="x-region-id")]]
