"""Convert SLURM configuration to Flow TaskConfig."""

import logging
from typing import Any, Dict, List, Optional

from flow._internal.frontends.slurm.parser import (
    SlurmConfig,
    parse_memory_to_gb,
    parse_time_to_hours,
)
from flow.api.models import TaskConfig

logger = logging.getLogger(__name__)


class SlurmToFlowConverter:
    """Convert SLURM configuration to Flow TaskConfig."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.slurm_config = self.config.get("slurm", {})

    def convert(self, slurm_config: SlurmConfig) -> TaskConfig:
        """Convert SLURM config to Flow TaskConfig.

        Args:
            slurm_config: Parsed SLURM configuration

        Returns:
            Flow TaskConfig
        """
        # Build the startup script with all the SLURM setup
        startup_script = self._build_startup_script(slurm_config)

        # Start with basic config - using script field for SLURM compatibility
        task_config = TaskConfig(
            name=slurm_config.job_name or "slurm-job",
            num_instances=slurm_config.nodes,
            command=startup_script,  # Use script field for full SLURM script
            instance_type="a100",  # Default instance type
        )

        # Map partition to region/instance type
        if slurm_config.partition:
            self._map_partition(slurm_config.partition, task_config)

        # Set resource requirements
        self._set_resources(slurm_config, task_config)

        # Set time limit as max runtime
        if slurm_config.time:
            hours = parse_time_to_hours(slurm_config.time)
            task_config.max_run_time_hours = hours
            task_config.max_price_per_hour = 100.0  # High limit to ensure job runs

        # Set container image based on modules
        if slurm_config.modules:
            task_config.image = self._map_modules_to_container(slurm_config.modules)

        # Set environment variables
        if slurm_config.environment:
            task_config.env = slurm_config.environment.copy()
        else:
            task_config.env = {}

        # Handle working directory
        if slurm_config.working_directory:
            task_config.working_dir = slurm_config.working_directory
            task_config.env["SLURM_WORKING_DIR"] = slurm_config.working_directory

        # Add SLURM compatibility environment variables
        self._add_slurm_env_vars(slurm_config, task_config)

        logger.info(f"Converted SLURM job '{slurm_config.job_name}' to Flow task")

        return task_config

    def _map_partition(self, partition: str, task_config: TaskConfig) -> None:
        """Map SLURM partition to Flow region and instance type.

        Args:
            partition: SLURM partition name
            task_config: TaskConfig to update
        """
        partition_map = self.slurm_config.get("partitions", {})

        if partition in partition_map:
            mapping = partition_map[partition]
            if "region" in mapping:
                task_config.region = mapping["region"]
            if "instance_type" in mapping:
                task_config.instance_type = mapping["instance_type"]
            logger.debug(
                f"Mapped partition '{partition}' to region '{task_config.region}', "
                f"instance type '{task_config.instance_type}'"
            )
        else:
            logger.warning(f"Unknown partition '{partition}', using defaults")

    def _set_resources(self, slurm_config: SlurmConfig, task_config: TaskConfig) -> None:
        """Set resource requirements from SLURM config.

        Args:
            slurm_config: SLURM configuration
            task_config: TaskConfig to update
        """
        # CPU resources - Flow v2 doesn't have explicit CPU field,
        # it's determined by instance type
        total_cpus = slurm_config.ntasks * slurm_config.cpus_per_task

        # Memory resources - Flow v2 doesn't have explicit memory field,
        # it's determined by instance type
        total_memory_gb = 16  # Default
        if slurm_config.mem:
            total_memory_gb = int(parse_memory_to_gb(slurm_config.mem))
        elif slurm_config.mem_per_cpu:
            mem_per_cpu_gb = parse_memory_to_gb(slurm_config.mem_per_cpu)
            total_memory_gb = int(mem_per_cpu_gb * total_cpus)

        # GPU resources → map to Flow instance_type convention (e.g., "4xa100")
        if slurm_config.gpus:
            base_gpu = (
                self._normalize_gpu_type(slurm_config.instance_type)
                if getattr(slurm_config, "instance_type", None)
                else "a100"
            )
            count = int(slurm_config.gpus)
            if count <= 1:
                task_config.instance_type = base_gpu
            else:
                task_config.instance_type = f"{count}x{base_gpu}"

    def _normalize_gpu_type(self, gpu_type: str) -> str:
        """Normalize GPU type names between SLURM and Flow.

        Args:
            gpu_type: SLURM GPU type

        Returns:
            Flow GPU type (lowercase)
        """
        # Normalize to lowercase and strip common prefixes/suffixes
        normalized = (gpu_type or "").strip().lower()
        # Map common aliases
        alias_map = {
            "a100-80gb": "a100",
            "h100-80gb": "h100",
            "nvidia-a100": "a100",
            "nvidia-h100": "h100",
        }
        return alias_map.get(normalized, normalized)

    def _map_modules_to_container(self, modules: List[str]) -> str:
        """Map module loads to container image.

        Args:
            modules: List of loaded modules

        Returns:
            Container image name
        """
        module_map = self.slurm_config.get("module_mapping", {})

        # Check each module for a mapping
        for module in modules:
            # Handle module with version (e.g., "python/3.9")
            base_module = module.split("/")[0]

            if module in module_map:
                return module_map[module]
            elif base_module in module_map:
                return module_map[base_module]

        # Default containers based on common modules
        for module in modules:
            if "python" in module.lower():
                return "python:3.9-slim"
            elif "cuda" in module.lower():
                return "nvidia/cuda:11.8.0-runtime-ubuntu22.04"
            elif "pytorch" in module.lower():
                return "pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime"
            elif "tensorflow" in module.lower():
                return "tensorflow/tensorflow:2.13.0-gpu"

        # Default container
        return "ubuntu:22.04"

    def _build_startup_script(self, slurm_config: SlurmConfig) -> str:
        """Build startup script from SLURM script content.

        Args:
            slurm_config: SLURM configuration

        Returns:
            Startup script for Flow
        """
        script_lines = ["#!/bin/bash", "set -e"]

        # Change to working directory if specified
        if slurm_config.working_directory:
            script_lines.append(f"cd {slurm_config.working_directory}")

        # Set up output redirection if specified
        if slurm_config.output:
            output_file = slurm_config.output.replace("%j", "$FLOW_TASK_ID")
            script_lines.append(f"exec 1> >(tee -a {output_file})")

        if slurm_config.error:
            error_file = slurm_config.error.replace("%j", "$FLOW_TASK_ID")
            script_lines.append(f"exec 2> >(tee -a {error_file} >&2)")

        # Add the actual script content
        script_lines.append("")
        script_lines.append("# User script")
        if slurm_config.script_content:
            script_lines.append(slurm_config.script_content)
        else:
            # If no script content, just add a placeholder
            script_lines.append("echo 'No script content provided'")

        return "\n".join(script_lines)

    def _add_slurm_env_vars(self, slurm_config: SlurmConfig, task_config: TaskConfig) -> None:
        """Add SLURM compatibility environment variables.

        Args:
            slurm_config: SLURM configuration
            task_config: TaskConfig to update
        """
        # Set SLURM environment variables for compatibility
        env = task_config.env

        env["SLURM_JOB_NAME"] = slurm_config.job_name or "flow-job"
        env["SLURM_JOB_ID"] = "$FLOW_TASK_ID"
        env["SLURM_NTASKS"] = str(slurm_config.ntasks)
        env["SLURM_CPUS_PER_TASK"] = str(slurm_config.cpus_per_task)
        env["SLURM_NNODES"] = str(slurm_config.nodes)

        if slurm_config.partition:
            env["SLURM_JOB_PARTITION"] = slurm_config.partition

        if slurm_config.gpus:
            env["SLURM_GPUS"] = str(slurm_config.gpus)

        # Array job variables
        if slurm_config.array:
            # This will be handled by the backend when expanding array jobs
            env["SLURM_ARRAY_JOB_ID"] = "$FLOW_TASK_ID"
            env["SLURM_ARRAY_TASK_ID"] = "$FLOW_ARRAY_INDEX"
