
from __future__ import annotations

from typing import List, Union, Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._types import Base64FileInput
from ..._utils import PropertyInfo

__all__ = ["HighlvlvpcCreateInstanceParams"]


class HighlvlvpcCreateInstanceParams(TypedDict, total=False):
    image_krn: Required[str]

    instance_name: Required[Annotated[str, PropertyInfo(alias="instanceName")]]

    instance_type: Required[Annotated[str, PropertyInfo(alias="instanceType")]]

    network_id: Required[str]

    region: Required[str]

    security_groups: Required[List[str]]

    sshkey_name: Required[str]

    subnet_id: Required[str]

    vm_volume_disk_size: Required[str]

    vpc_id: Required[str]

    k_customer_id: Required[Annotated[str, PropertyInfo(alias="k-customer-id")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]

    floating_ip: bool

    security_group_rules_name: str

    security_group_rules_port: str

    security_group_rules_protocol: str

    user_data: Annotated[Union[str, Base64FileInput], PropertyInfo(format="base64")]

    volume_name: Optional[str]

    volume_size: Optional[str]
