"""Mithril resource management.

This package manages Mithril resources:
- GPU specifications and capabilities
- Project name to ID resolution
- SSH key management
"""

from flow.providers.mithril.resources.gpu import GPU_SPECS, get_default_gpu_memory
from flow.providers.mithril.resources.projects import ProjectNotFoundError, ProjectResolver
from flow.providers.mithril.resources.ssh import SSHKeyError, SSHKeyManager, SSHKeyNotFoundError

__all__ = [
    # GPU
    "GPU_SPECS",
    "get_default_gpu_memory",
    # Projects
    "ProjectResolver",
    "ProjectNotFoundError",
    # SSH
    "SSHKeyManager",
    "SSHKeyError",
    "SSHKeyNotFoundError",
]
