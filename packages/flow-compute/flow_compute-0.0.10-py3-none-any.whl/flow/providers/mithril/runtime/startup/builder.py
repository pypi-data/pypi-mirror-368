"""Startup script builder with clean separation of concerns.

This implementation provides:
- Independent, testable script sections
- Abstracted template rendering
- Separate compression handling
- Explicit validation
- Clear orchestration without implementation details
"""

import base64
import gzip
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from flow.api.models import TaskConfig

from ...core.constants import STARTUP_SCRIPT_MAX_SIZE
from .sections import (
    CodeUploadSection,
    CompletionSection,
    DevVMDockerSection,
    DockerSection,
    GPUdHealthSection,
    HeaderSection,
    IScriptSection,
    PortForwardingSection,
    S3Section,
    ScriptContext,
    UserScriptSection,
    VolumeSection,
    WorkloadResumeSection,
)
from .templates import ITemplateEngine, create_template_engine


@dataclass
class StartupScript:
    """Structured representation of a startup script."""

    content: str
    compressed: bool = False
    sections: List[str] = None
    validation_errors: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        self.sections = self.sections or []
        self.validation_errors = self.validation_errors or []
        self.metadata = self.metadata or {}

    @property
    def is_valid(self) -> bool:
        """Check if the script is valid (no validation errors)."""
        return not self.validation_errors

    @property
    def size_bytes(self) -> int:
        """Get the size of the script content in bytes."""
        return len(self.content.encode("utf-8"))


class IScriptCompressor(Protocol):
    """Protocol for script compression strategies."""

    def should_compress(self, content: str, max_size: int) -> bool:
        """Determine if compression is needed."""
        ...

    def compress(self, content: str) -> str:
        """Compress the script content."""
        ...


class GzipCompressor:
    """Gzip-based script compression."""

    def should_compress(self, content: str, max_size: int) -> bool:
        """Check if content exceeds max size."""
        return len(content.encode("utf-8")) > max_size

    def compress(self, content: str) -> str:
        """Compress and create bootstrap script."""
        compressed = gzip.compress(content.encode("utf-8"))
        encoded = base64.b64encode(compressed).decode("ascii")

        # Create bootstrap script that decompresses and executes
        return f"""#!/bin/bash
# Bootstrap script for compressed startup script
# Original size: {len(content)} bytes
# Compressed size: {len(compressed)} bytes

set -euo pipefail

echo "Decompressing and executing startup script..."
echo "{encoded}" | base64 -d | gunzip | bash
"""


class IScriptBuilder(Protocol):
    """Protocol for startup script builders."""

    def build(self, config: TaskConfig) -> StartupScript:
        """Build a startup script from configuration."""
        ...


class StartupScriptBuilder:
    """Orchestrates startup script generation with clean architecture."""

    def __init__(
        self,
        sections: Optional[List[IScriptSection]] = None,
        template_engine: Optional[ITemplateEngine] = None,
        compressor: Optional[IScriptCompressor] = None,
        max_uncompressed_size: int = STARTUP_SCRIPT_MAX_SIZE,
    ):
        """Initialize builder with dependencies.

        Args:
            sections: List of script sections (uses defaults if None)
            template_engine: Template engine for rendering
            compressor: Compression strategy
            max_uncompressed_size: Maximum size before compression
        """
        self.sections = sections or self._default_sections()
        self.template_engine = template_engine or create_template_engine("simple")
        self.compressor = compressor or GzipCompressor()
        self.max_uncompressed_size = max_uncompressed_size

    def _default_sections(self) -> List[IScriptSection]:
        """Get default script sections in priority order."""
        from .sections import RuntimeMonitorSection

        return [
            HeaderSection(),
            PortForwardingSection(),
            VolumeSection(),
            S3Section(),
            DevVMDockerSection(),  # Docker for dev VMs (without containers)
            GPUdHealthSection(),  # Added GPUd health monitoring
            CodeUploadSection(),
            DockerSection(),
            UserScriptSection(),
            WorkloadResumeSection(),
            RuntimeMonitorSection(),  # Runtime limit monitoring
            CompletionSection(),
        ]

    def build(self, config: TaskConfig) -> StartupScript:
        """Build startup script from task configuration.

        This method orchestrates the script generation process:
        1. Creates context from config
        2. Validates all sections
        3. Generates content from each section
        4. Combines sections
        5. Compresses if needed

        Args:
            config: Task configuration

        Returns:
            StartupScript with content and metadata
        """
        # Create context from config
        context = self._create_context(config)

        # Validate all sections
        validation_errors = self._validate_sections(context)
        if validation_errors:
            return StartupScript(
                content="",
                validation_errors=validation_errors,
                metadata={"config": config.model_dump()},
            )

        # Generate sections
        section_contents = self._generate_sections(context)

        # Combine sections
        full_content = self._combine_sections(section_contents)

        # Add debug logging
        import logging

        logger = logging.getLogger(__name__)
        logger.debug("=" * 80)
        logger.debug("STARTUP SCRIPT CONTENT:")
        logger.debug("=" * 80)
        logger.debug(f"Sections included: {[s['name'] for s in section_contents]}")
        logger.debug(f"Script size: {len(full_content.encode('utf-8'))} bytes")
        logger.debug("--- Script Content ---")
        logger.debug(full_content)
        logger.debug("--- End Script Content ---")
        logger.debug("=" * 80)

        # Compress if needed
        compressed = False
        original_size = len(full_content.encode("utf-8"))
        if self.compressor.should_compress(full_content, self.max_uncompressed_size):
            full_content = self.compressor.compress(full_content)
            compressed = True
            logger.debug(f"Script compressed. New size: {len(full_content.encode('utf-8'))} bytes")

        return StartupScript(
            content=full_content,
            compressed=compressed,
            sections=[s["name"] for s in section_contents],
            metadata={
                "config": config.model_dump(),
                "original_size": original_size,
                "section_count": len(section_contents),
            },
        )

    def _create_context(self, config: TaskConfig) -> ScriptContext:
        """Create script context from task configuration."""
        # Extract code archive from environment if present
        env = config.env.copy() if config.env else {}
        code_archive = env.pop("_FLOW_CODE_ARCHIVE", None)

        # Determine command type and set appropriate context fields
        docker_command = None
        user_script = None

        if isinstance(config.command, list):
            # List form - use as docker command
            docker_command = config.command
        elif isinstance(config.command, str):
            # String form - always treat as docker command
            # Commands run inside Docker, including scripts with shebangs
            if config.command.strip():
                # For any command (single or multi-line), preserve as-is
                # Docker will handle script execution properly
                docker_command = [config.command]

        return ScriptContext(
            ports=[],  # TaskConfig doesn't have ports field
            volumes=[v.model_dump() for v in config.volumes] if config.volumes else [],
            docker_image=config.image,  # Changed from docker_image
            docker_command=docker_command,
            user_script=user_script,
            environment=env,  # Environment without the code archive
            upload_code=config.upload_code,
            code_archive=code_archive,
            instance_type=config.instance_type,  # Pass instance type for GPU detection
            task_id=getattr(config, "task_id", None),  # Pass task ID if available
            task_name=config.name,  # Pass task name for identification
            enable_workload_resume=getattr(
                config, "enable_workload_resume", True
            ),  # Enable by default
            # Runtime limit fields
            max_run_time_hours=config.max_run_time_hours,
            min_run_time_hours=config.min_run_time_hours,
            deadline_hours=config.deadline_hours,
        )

    def _validate_sections(self, context: ScriptContext) -> List[str]:
        """Validate all sections and collect errors."""
        all_errors = []

        for section in sorted(self.sections, key=lambda s: s.priority):
            if section.should_include(context):
                errors = section.validate(context)
                if errors:
                    all_errors.extend([f"{section.name}: {e}" for e in errors])

        return all_errors

    def _generate_sections(self, context: ScriptContext) -> List[Dict[str, Any]]:
        """Generate content for all applicable sections."""
        section_contents = []

        for section in sorted(self.sections, key=lambda s: s.priority):
            if section.should_include(context):
                content = section.generate(context)
                if content.strip():  # Only include non-empty sections
                    section_contents.append(
                        {
                            "name": section.name,
                            "priority": section.priority,
                            "content": content,
                        }
                    )

        return section_contents

    def _combine_sections(self, sections: List[Dict[str, Any]]) -> str:
        """Combine section contents into final script."""
        if not sections:
            return "#!/bin/bash\n# Empty startup script\n"

        # Combine sections with simple spacing
        combined = []
        for i, section in enumerate(sections):
            combined.append(section["content"])
            # Add spacing between sections (but not after the last one)
            if i < len(sections) - 1:
                combined.append("")

        return "\n".join(combined)


class MithrilStartupScriptBuilder(StartupScriptBuilder):
    """Mithril-specific startup script builder.

    This is a convenience class that configures the builder
    with Mithril-specific defaults and behaviors.
    """

    def __init__(self):
        """Initialize with Mithril-specific configuration."""
        super().__init__(
            sections=self._mithril_sections(),
            template_engine=create_template_engine("simple"),
            compressor=GzipCompressor(),
            max_uncompressed_size=STARTUP_SCRIPT_MAX_SIZE,
        )

    def _mithril_sections(self) -> List[IScriptSection]:
        """Get Mithril-specific script sections."""
        # For now, use default sections
        # Could add Mithril-specific sections here
        return self._default_sections()


# For backward compatibility
def build_mithril_startup_script(config: TaskConfig) -> str:
    """Build an Mithril startup script from task configuration.

    This is a convenience function for simple use cases.

    Args:
        config: Task configuration

    Returns:
        Startup script content as string

    Raises:
        ValueError: If validation fails
    """
    builder = MithrilStartupScriptBuilder()
    script = builder.build(config)

    if not script.is_valid:
        raise ValueError(f"Invalid configuration: {', '.join(script.validation_errors)}")

    return script.content
