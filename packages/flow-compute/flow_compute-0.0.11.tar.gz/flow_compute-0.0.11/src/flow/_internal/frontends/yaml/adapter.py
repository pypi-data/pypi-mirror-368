"""YAML frontend adapter for Flow SDK."""

import logging
import uuid
from pathlib import Path
from typing import Any, Dict, Union

import yaml

from flow._internal.frontends.base import BaseFrontendAdapter
from flow._internal.frontends.registry import FrontendRegistry
from flow.api.models import TaskConfig
from flow.errors import ValidationError

logger = logging.getLogger(__name__)


@FrontendRegistry.register("yaml")
class YamlFrontendAdapter(BaseFrontendAdapter):
    """YAML frontend adapter.

    Parses YAML configuration files into Flow TaskConfig.
    """

    def __init__(self):
        super().__init__("yaml")

    async def parse_and_convert(
        self, input_data: Union[str, Path, Dict], **options: Any
    ) -> TaskConfig:
        """Parse YAML file and convert to TaskConfig.

        Args:
            input_data: Path to YAML file or dict of YAML data
            **options: Additional options (overrides YAML values)

        Returns:
            TaskConfig object
        """
        # Validate input type
        if not isinstance(input_data, (str, Path, dict)):
            raise ValidationError("Input must be a file path or dictionary")

        # Load YAML data
        if isinstance(input_data, dict):
            # Already parsed dict
            yaml_data = input_data
        else:
            # Load from file
            yaml_data = self._load_yaml_file(input_data)

        # Convert from YAML format to TaskConfig format
        task_data = self._convert_yaml_to_taskconfig(yaml_data)

        # Apply any overrides from options
        for key, value in options.items():
            if value is not None:
                task_data[key] = value

        # Create TaskConfig
        try:
            task_config = TaskConfig(**task_data)
            logger.info(f"Parsed YAML config for task '{task_config.name}'")
            return task_config
        except Exception as e:
            raise ValidationError(f"Invalid YAML configuration: {e}")

    def _load_yaml_file(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load YAML file and return parsed data.

        Args:
            path: Path to YAML file

        Returns:
            Parsed YAML data as dict
        """
        path = Path(path)
        if not path.exists():
            raise ValidationError(f"File not found: {path}")

        try:
            with open(path) as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                raise ValidationError("YAML file must contain a dictionary at root level")

            return data
        except yaml.YAMLError as e:
            raise ValidationError(f"Invalid YAML syntax: {e}")

    def _convert_yaml_to_taskconfig(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert YAML format to TaskConfig format.

        Handles the mapping between the human-friendly YAML format
        and the TaskConfig model.

        Args:
            data: YAML data dict

        Returns:
            Dict suitable for TaskConfig initialization
        """
        result = {}

        # Required fields
        if "name" not in data:
            raise ValidationError("Missing required field: name")

        # Add unique suffix to name if requested
        name = data["name"]
        if data.get("unique_name", False) or data.get("append_suffix", False):
            # Generate a short unique suffix
            suffix = uuid.uuid4().hex[:6]
            name = f"{name}-{suffix}"

        result["name"] = name

        # Handle image/docker_image mapping
        if "image" in data:
            result["image"] = data["image"]
        elif "docker_image" in data:
            result["image"] = data["docker_image"]
        else:
            raise ValidationError("Missing required field: image or docker_image")

        # Handle command fields - unified into single 'command' field
        # Priority: command > script > startup_script > shell
        if "command" in data:
            result["command"] = data["command"]
        elif "script" in data:
            logger.warning(
                "The 'script' field is deprecated and will be removed in v2.0.0. "
                "Please use 'command' instead."
            )
            result["command"] = data["script"]
        elif "startup_script" in data:
            logger.warning(
                "The 'startup_script' field is deprecated and will be removed in v2.0.0. "
                "Please use 'command' instead."
            )
            result["command"] = data["startup_script"]
        elif "shell" in data:
            logger.warning(
                "The 'shell' field is deprecated and will be removed in v2.0.0. "
                "Please use 'command' instead."
            )
            result["command"] = data["shell"]

        # Handle resources section
        if "resources" in data:
            resources = data["resources"]

            # NOTE: num_gpus and gpu_type are not direct TaskConfig fields
            # They could be used to construct instance_type, but for now
            # we'll skip them since test expects instance_type to be set separately

            # Handle storage/disk -> volumes
            if "disk" in resources or "storage" in resources:
                disk_size = resources.get("disk", resources.get("storage", "100GB"))
                # Parse size (e.g., "100GB" -> 100)
                size_gb = int(disk_size.replace("GB", "").strip())
                result["volumes"] = [
                    {"size_gb": size_gb, "mount_path": "/data", "interface": "block"}
                ]

        # Handle top-level cpu/memory/gpu/storage (legacy format)
        if "cpu" in data:
            # CPU is not directly mapped to TaskConfig
            pass
        if "memory" in data:
            # Memory is not directly mapped to TaskConfig
            pass
        if "gpu" in data:
            # NOTE: gpu count is not a direct field in TaskConfig
            # For legacy support, we'll set a default instance_type if not specified
            if "instance_type" not in result and "instance_type" not in data:
                result["instance_type"] = "gpu.nvidia.h100"  # Default GPU instance
        if "storage" in data:
            # Parse size
            size_gb = int(data["storage"].replace("GB", "").strip())
            result["volumes"] = [{"size_gb": size_gb, "mount_path": "/data", "interface": "block"}]

        # Handle env -> env
        if "env" in data:
            result["env"] = data["env"]
        elif "environment" in data:
            result["env"] = data["environment"]

        # Handle ports - TaskConfig doesn't have a ports field anymore
        # We could store this in environment or script if needed
        if "ports" in data:
            # For now, just skip ports as TaskConfig doesn't support them
            pass
        elif "port" in data:
            # Support single port field - also skip
            pass

        # Handle input/output sections - store as metadata in startup script
        if "input" in data or "output" in data:
            # For now, we'll store these in the startup script as comments
            # In a real implementation, these would be handled by the task runner
            input_spec = data.get("input", {})
            output_spec = data.get("output", {})
            script_additions = []

            if input_spec and isinstance(input_spec, dict):
                if "source" in input_spec and "destination" in input_spec:
                    script_additions.append(
                        f"# INPUT: {input_spec['source']} -> {input_spec['destination']}"
                    )

            if output_spec and isinstance(output_spec, dict):
                if "source" in output_spec and "destination" in output_spec:
                    script_additions.append(
                        f"# OUTPUT: {output_spec['source']} -> {output_spec['destination']}"
                    )

            if script_additions and "command" in result:
                # Prepend I/O metadata to command if it's a string
                if isinstance(result["command"], str):
                    result["command"] = "\n".join(script_additions) + "\n" + result["command"]
            # Don't create a command field just for I/O metadata if no command exists

        # Copy over other supported fields directly
        for field in ["instance_type", "num_instances", "region", "max_price_per_hour", "ssh_keys"]:
            if field in data:
                # No need to skip instance_type anymore since we don't set num_gpus/gpu_type
                result[field] = data[field]

        return result

    async def validate(self, input_data: Union[str, Path, Dict]) -> bool:
        """Validate YAML configuration.

        Args:
            input_data: Path to YAML file or dict of YAML data

        Returns:
            True if valid, False otherwise
        """
        try:
            await self.parse_and_convert(input_data)
            return True
        except Exception:
            return False

    def format_job_id(self, flow_job_id: str) -> str:
        """Format Flow job ID for YAML display.

        Args:
            flow_job_id: Internal Flow job ID

        Returns:
            Same job ID (no transformation needed)
        """
        return flow_job_id

    def format_status(self, flow_status: str) -> str:
        """Format Flow status for YAML display.

        Args:
            flow_status: Flow status

        Returns:
            Same status (no transformation needed)
        """
        return flow_status

    @property
    def version(self) -> str:
        """Get adapter version."""
        return "1.0.0"

    @property
    def capabilities(self) -> Dict[str, Any]:
        """Get adapter capabilities."""
        return {
            "supports_file": True,
            "supports_dict": True,
        }
