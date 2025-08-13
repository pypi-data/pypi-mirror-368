

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from krutrim_client._utils import PropertyInfo

__all__ = ["V1DetachRuleParams"]


class V1DetachRuleParams(TypedDict, total=False):
    ruleid: Required[str]
    """KRN of the Security Group Rule."""

    securityid: Required[str]
    """KRN of the Security Group to attach/detach the rule from."""

    vpcid: Required[str]
    """KRN of the VPC associated with the Security Group and rule."""

    k_customer_id: Required[Annotated[str, PropertyInfo(alias="K-Customer-ID")]]

    x_account_id: Required[Annotated[str, PropertyInfo(alias="x-account-id")]]
