# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from krutrim_client._utils import PropertyInfo

__all__ = ["SecurityGroupListByVpcParams"]


class SecurityGroupListByVpcParams(TypedDict, total=False):
    x_region: Required[Annotated[str, PropertyInfo(alias="x-region")]]

    limit: int
    """The maximum number of records to return (for pagination)."""

    offset: int
    """The number of records to skip from the beginning of the list (for pagination)."""
