"""Mithril resource management.

This package manages Mithril resources:
- GPU specifications and capabilities
- Project name to ID resolution
- SSH key management
"""

from .gpu import get_default_gpu_memory, GPU_SPECS
from .projects import ProjectNotFoundError, ProjectResolver
from .ssh import SSHKeyError, SSHKeyManager, SSHKeyNotFoundError

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
