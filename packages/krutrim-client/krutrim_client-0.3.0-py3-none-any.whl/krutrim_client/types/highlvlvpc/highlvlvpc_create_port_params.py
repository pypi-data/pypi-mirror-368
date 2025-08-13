
from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcCreatePortParams"]


class HighlvlvpcCreatePortParams(TypedDict, total=False):
    floating_ip: Required[bool]
    """Whether to allocate and associate a new floating IP to this port."""

    name: Required[str]
    """Name for the new port."""

    network_id: Required[str]
    """The KRN of the network to associate with the port."""

    subnet_id: Required[str]
    """The KRN of the subnet to associate with the port and assign an IP from."""

    vpc_id: Required[str]
    """The KRN of the VPC where the port will be created."""

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]
