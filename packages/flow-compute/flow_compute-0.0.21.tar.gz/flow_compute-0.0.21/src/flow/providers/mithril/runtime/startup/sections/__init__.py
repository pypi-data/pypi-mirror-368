"""Modular section exports.

This module re-exports section classes from the legacy `sections.py` to provide
a per-file structure while maintaining backward-compatible imports like:

    from flow.providers.mithril.runtime.startup.sections import HeaderSection

Sections are also available individually via submodules, e.g.:

    from flow.providers.mithril.runtime.startup.sections.header import HeaderSection
"""

from flow.providers.mithril.runtime.startup.sections.base import (
    IScriptSection,
    ScriptContext,
    ScriptSection,
)
from flow.providers.mithril.runtime.startup.sections.code_upload import (
    CodeUploadSection,
)
from flow.providers.mithril.runtime.startup.sections.completion import CompletionSection
from flow.providers.mithril.runtime.startup.sections.dev_vm_docker import (
    DevVMDockerSection,
)
from flow.providers.mithril.runtime.startup.sections.docker import DockerSection
from flow.providers.mithril.runtime.startup.sections.gpud_health import (
    GPUdHealthSection,
)
from flow.providers.mithril.runtime.startup.sections.header import HeaderSection
from flow.providers.mithril.runtime.startup.sections.port_forwarding import (
    PortForwardingSection,
)
from flow.providers.mithril.runtime.startup.sections.rendezvous import (
    RendezvousSection,
)
from flow.providers.mithril.runtime.startup.sections.runtime_monitor import (
    RuntimeMonitorSection,
)
from flow.providers.mithril.runtime.startup.sections.s3 import S3Section
from flow.providers.mithril.runtime.startup.sections.user_script import UserScriptSection
from flow.providers.mithril.runtime.startup.sections.volume import VolumeSection
from flow.providers.mithril.runtime.startup.sections.workload_resume import (
    WorkloadResumeSection,
)
from flow.providers.mithril.runtime.startup.sections.slurm_setup import (
    SlurmSetupSection,
)

__all__ = [
    "ScriptContext",
    "IScriptSection",
    "ScriptSection",
    "HeaderSection",
    # Re-export modularized sections
    "S3Section",
    "PortForwardingSection",
    "VolumeSection",
    "CodeUploadSection",
    "DevVMDockerSection",
    "DockerSection",
    "UserScriptSection",
    "WorkloadResumeSection",
    "GPUdHealthSection",
    "RuntimeMonitorSection",
    "CompletionSection",
    "RendezvousSection",
    "SlurmSetupSection",
]
