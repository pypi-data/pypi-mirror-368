"""Frontend adapters for Flow SDK.

Frontend adapters parse different input formats (SLURM scripts, Submitit calls, etc.)
into the common Flow TaskConfig intermediate representation.
"""

from flow._internal.frontends.base import BaseFrontendAdapter
from flow._internal.frontends.registry import FrontendRegistry

__all__ = ["BaseFrontendAdapter", "FrontendRegistry"]
