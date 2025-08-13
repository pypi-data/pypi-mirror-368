from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["PodUpdateParams"]


class PodUpdateParams(TypedDict, total=False):
    action: Required[Literal["start", "stop", "restart"]]
    """The action to perform on the kpod."""
