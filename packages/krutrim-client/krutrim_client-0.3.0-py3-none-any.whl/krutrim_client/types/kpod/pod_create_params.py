from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

__all__ = ["PodCreateParams"]


class PodCreateParams(TypedDict, total=False):
    container_disk_size: Required[str]
    """The size of the container disk in GB."""

    expose_http_ports: Required[str]
    """Comma-separated list of HTTP ports to expose (e.g., "8888")."""

    expose_tcp_ports: Required[str]
    """Comma-separated list of TCP ports to expose (e.g., "22")."""

    flavor_name: Required[str]
    """The name of the flavor/instance type for the pod (e.g., GPU type)."""

    has_encrypt_volume: Required[bool]
    """Indicates if the volume should be encrypted."""

    has_jupyter_notebook: Required[bool]
    """Indicates if Jupyter Notebook should be enabled."""

    has_ssh_access: Required[bool]
    """Indicates if SSH access should be enabled."""

    pod_name: Required[str]
    """Unique name for the pod."""

    pod_template_id: Required[int]
    """The ID of the pod template to use."""

    region: Required[str]
    """The region where the pod should be deployed."""

    sshkey_name: Required[str]
    """The name of the SSH key to associate with the pod."""

    volume_disk_size: Required[str]
    """The size of the attached volume disk in GB."""

    volume_mount_path: Required[str]
    """The path where the volume should be mounted inside the pod."""

    environment_variables: Iterable[object]
    """List of environment variables to set in the pod."""
