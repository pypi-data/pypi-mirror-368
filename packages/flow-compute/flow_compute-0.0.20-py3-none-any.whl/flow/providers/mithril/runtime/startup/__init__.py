"""Mithril startup script generation.

This package builds startup scripts for Mithril instances:
- Main builder orchestration
- Modular script sections
- Template engine abstraction
"""

from flow.providers.mithril.runtime.startup.builder import (
    MithrilStartupScriptBuilder,
    StartupScript,
)
from flow.providers.mithril.runtime.startup.sections import (
    CodeUploadSection,
    DockerSection,
    HeaderSection,
    S3Section,
    ScriptContext,
    UserScriptSection,
    VolumeSection,
)
from flow.providers.mithril.runtime.startup.templates import ITemplateEngine, create_template_engine

__all__ = [
    # Builder
    "MithrilStartupScriptBuilder",
    "StartupScript",
    # Sections
    "ScriptContext",
    "HeaderSection",
    "VolumeSection",
    "S3Section",
    "DockerSection",
    "CodeUploadSection",
    "UserScriptSection",
    # Templates
    "ITemplateEngine",
    "create_template_engine",
]
