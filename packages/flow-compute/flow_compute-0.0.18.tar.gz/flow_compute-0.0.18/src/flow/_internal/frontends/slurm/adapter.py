"""SLURM frontend adapter for Flow SDK."""

import logging
from pathlib import Path
from typing import Any, List, Union

from flow._internal.frontends.base import BaseFrontendAdapter
from flow._internal.frontends.registry import FrontendRegistry
from flow._internal.frontends.slurm.converter import SlurmToFlowConverter
from flow._internal.frontends.slurm.parser import parse_sbatch_script, parse_slurm_options
from flow.api.models import TaskConfig

logger = logging.getLogger(__name__)


@FrontendRegistry.register("slurm")
class SlurmFrontendAdapter(BaseFrontendAdapter):
    """SLURM frontend adapter.

    Parses SLURM batch scripts and command-line options into Flow TaskConfig.
    """

    def __init__(self, name: str = "slurm"):
        super().__init__(name)
        self.converter = SlurmToFlowConverter()

        # SLURM job ID counter for compatibility
        self._job_counter = 1000

    async def parse_and_convert(self, input_data: Union[str, Path], **options: Any) -> TaskConfig:
        """Parse SLURM script and convert to TaskConfig.

        Args:
            input_data: Path to SLURM batch script
            **options: SLURM command-line options (override script directives)

        Returns:
            TaskConfig intermediate representation
        """
        # Parse script
        script_path = str(input_data)
        slurm_config = parse_sbatch_script(script_path)

        # Apply command-line options (they override script directives)
        if options:
            cli_config = parse_slurm_options(options)
            # Merge configs, CLI takes precedence
            for attr, value in cli_config.__dict__.items():
                if value is not None and value != {} and value != []:
                    setattr(slurm_config, attr, value)

        # Convert to Flow TaskConfig
        task_config = self.converter.convert(slurm_config)

        logger.info(f"Parsed SLURM script '{script_path}' -> job '{task_config.name}'")

        return task_config

    async def parse_array_job(
        self, input_data: Union[str, Path], **options: Any
    ) -> List[TaskConfig]:
        """Parse SLURM array job and return list of TaskConfigs.

        Args:
            input_data: Path to SLURM batch script
            **options: SLURM command-line options

        Returns:
            List of TaskConfig objects for array tasks
        """
        # Parse base configuration
        base_config = await self.parse_and_convert(input_data, **options)

        # Get array specification
        slurm_config = parse_sbatch_script(str(input_data))
        if options:
            cli_config = parse_slurm_options(options)
            if cli_config.array:
                slurm_config.array = cli_config.array

        if not slurm_config.array:
            return [base_config]

        # Parse array specification
        array_indices = self._parse_array_spec(slurm_config.array)

        # Create task configs for each array element
        task_configs = []
        for idx in array_indices:
            # Clone base config
            task_config = TaskConfig(**base_config.model_dump())

            # Customize for array task
            task_config.name = f"{task_config.name}_{idx}"
            task_config.env["SLURM_ARRAY_TASK_ID"] = str(idx)
            task_config.env["SLURM_ARRAY_JOB_ID"] = "$FLOW_JOB_ID"

            task_configs.append(task_config)

        logger.info(f"Parsed SLURM array job with {len(task_configs)} tasks")

        return task_configs

    def _parse_array_spec(self, array_spec: str) -> List[int]:
        """Parse SLURM array specification.

        Supports:
        - Range: 1-10
        - List: 1,3,5,7
        - Range with step: 1-10:2
        - Mixed: 1-5,10,15-20:2
        """
        indices = []

        for part in array_spec.split(","):
            if "-" in part:
                # Range format
                if ":" in part:
                    # Range with step
                    range_part, step = part.split(":", 1)
                    start, end = map(int, range_part.split("-", 1))
                    step = int(step)
                    indices.extend(range(start, end + 1, step))
                else:
                    # Simple range
                    start, end = map(int, part.split("-", 1))
                    indices.extend(range(start, end + 1))
            else:
                # Single number
                indices.append(int(part))

        return sorted(set(indices))

    def format_job_id(self, flow_job_id: str) -> str:
        """Format Flow job ID as SLURM job ID.

        Args:
            flow_job_id: Internal Flow job ID (e.g., "task_abc123")

        Returns:
            SLURM-style numeric job ID
        """
        # For compatibility, generate numeric ID
        job_id = self._job_counter
        self._job_counter += 1
        return str(job_id)

    def format_status(self, flow_status: str) -> str:
        """Format Flow status as SLURM status.

        Args:
            flow_status: Flow status (e.g., "running", "completed")

        Returns:
            SLURM status code (e.g., "R", "CD")
        """
        # Status mapping
        status_map = {
            "pending": "PD",
            "running": "R",
            "completed": "CD",
            "failed": "F",
            "cancelled": "CA",
            "timeout": "TO",
            "preempted": "PR",
        }

        return status_map.get(flow_status.lower(), "UN")
