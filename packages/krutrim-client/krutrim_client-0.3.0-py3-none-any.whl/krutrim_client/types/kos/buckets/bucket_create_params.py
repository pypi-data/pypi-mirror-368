from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from krutrim_client._utils import PropertyInfo 


__all__ = ["BucketCreateParams"]


class BucketCreateParams(TypedDict, total=False):
    name: Required[str]
    """The name of the bucket."""

    region: Required[str]
    """The region where the bucket will be created."""

    x_region_id: Required[Annotated[str, PropertyInfo(alias="x-region-id")]]

    anonymous_access: bool
    """Whether anonymous access is allowed for the bucket."""

    description: str
    """A description for the bucket."""

    tags: Dict[str, str]
    """Key-value tags associated with the bucket."""

    versioning: bool
    """Whether versioning is enabled for the bucket."""
