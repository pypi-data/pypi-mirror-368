# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["V1PerformActionParams"]


class V1PerformActionParams(TypedDict, total=False):
    action: Required[Literal["stop", "stop", "reboot"]]
    """The action to perform on the VM instance."""
