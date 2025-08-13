

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["InstanceInfo"]


class InstanceInfo(BaseModel):
    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)
    """Timestamp of when the instance was created."""

    floating_ip_address: Optional[str] = FieldInfo(alias="floatingIpAddress", default=None)
    """Floating IP address associated with the instance, if any."""

    image_krn: Optional[str] = None
    """KRN of the image used for the instance."""

    instance_id: Optional[str] = FieldInfo(alias="instanceId", default=None)
    """Unique identifier of the instance (often the KRN itself or a part of it)."""

    instance_name: Optional[str] = FieldInfo(alias="instanceName", default=None)
    """Name of the instance."""

    instance_type: Optional[str] = FieldInfo(alias="instanceType", default=None)
    """Type of the instance."""

    ip_address: Optional[str] = FieldInfo(alias="ipAddress", default=None)
    """Primary private IP address of the instance."""

    network_id: Optional[str] = FieldInfo(alias="networkId", default=None)
    """KRN of the network the instance is connected to."""

    region: Optional[str] = None
    """Region where the instance is located."""

    security_groups: Optional[List[str]] = None

    sshkey_name: Optional[str] = None
    """Name of the SSH key associated with the instance."""

    status: Optional[str] = None
    """Current status of the instance."""

    subnet_id: Optional[str] = FieldInfo(alias="subnetId", default=None)
    """KRN of the subnet the instance is part of."""

    vm_volume_disk_size: Optional[str] = None
    """Size of the root volume in GB."""

    vpc_id: Optional[str] = FieldInfo(alias="vpcId", default=None)
    """KRN of the VPC the instance belongs to."""
