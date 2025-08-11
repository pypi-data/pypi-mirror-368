"""SLURM script parser for extracting job configuration."""

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SlurmConfig:
    """Container for parsed SLURM configuration."""

    def __init__(self):
        self.job_name: str | None = None
        self.partition: str | None = None
        self.nodes: int = 1
        self.ntasks: int = 1
        self.ntasks_per_node: int | None = None
        self.cpus_per_task: int = 1
        self.mem: str | None = None  # e.g., "16G", "1024M"
        self.mem_per_cpu: str | None = None
        self.mem_per_gpu: str | None = None
        self.time: str | None = None  # e.g., "01:00:00", "2-00:00:00"
        self.gpus: int | None = None
        self.gpus_per_node: int | None = None
        self.gpus_per_task: int | None = None
        self.gpu_type: str | None = None
        # Explicit GPU type captured from --gpus=<type>:<count> or --gres=gpu:<type>:<count>
        # Named "instance_type" to align with Flow terminology downstream
        self.instance_type: str | None = None
        self.constraint: str | None = None
        self.array: str | None = None  # e.g., "1-10", "1,3,5,7"
        self.dependency: str | None = None  # e.g., "afterok:12345"
        self.qos: str | None = None
        self.account: str | None = None
        self.reservation: str | None = None
        self.output: str | None = None
        self.error: str | None = None
        self.mail_type: str | None = None
        self.mail_user: str | None = None
        self.working_directory: str | None = None
        self.environment: dict[str, str] = {}
        self.modules: list[str] = []
        self.script_content: str = ""
        self.raw_directives: dict[str, str] = {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {k: v for k, v in self.__dict__.items() if v is not None and v != {} and v != []}


def parse_sbatch_script(script_path: str) -> SlurmConfig:
    """Parse SLURM batch script to extract configuration.

    Args:
        script_path: Path to SLURM batch script

    Returns:
        Parsed SLURM configuration
    """
    config = SlurmConfig()

    script_path_obj = Path(script_path)
    if not script_path_obj.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    with open(script_path_obj) as f:
        lines = f.readlines()

    script_lines = []
    in_header = True

    for line in lines:
        line = line.strip()

        # Check if we're still in the header (SBATCH directives)
        if in_header and line.startswith("#SBATCH"):
            _parse_sbatch_directive(line, config)
        elif in_header and line and not line.startswith("#"):
            # First non-comment, non-empty line marks end of header
            in_header = False
            script_lines.append(line)
        elif not in_header:
            script_lines.append(line)

        # Look for module loads anywhere in the script
        if line.startswith("module load"):
            module = line.replace("module load", "").strip()
            if module:
                config.modules.append(module)

    config.script_content = "\n".join(script_lines)

    logger.debug(f"Parsed SLURM script {script_path}: {config.to_dict()}")

    return config


def parse_slurm_options(options: dict[str, Any]) -> SlurmConfig:
    """Parse SLURM options from command line arguments.

    Args:
        options: Dictionary of SLURM options

    Returns:
        Parsed SLURM configuration
    """
    config = SlurmConfig()

    # Direct mappings
    direct_mappings = {
        "job_name": "job_name",
        "partition": "partition",
        "nodes": "nodes",
        "ntasks": "ntasks",
        "ntasks_per_node": "ntasks_per_node",
        "cpus_per_task": "cpus_per_task",
        "mem": "mem",
        "mem_per_cpu": "mem_per_cpu",
        "mem_per_gpu": "mem_per_gpu",
        "time": "time",
        "constraint": "constraint",
        "array": "array",
        "dependency": "dependency",
        "output": "output",
        "error": "error",
        "mail_type": "mail_type",
        "mail_user": "mail_user",
        "chdir": "working_directory",
        "qos": "qos",
        "account": "account",
        "reservation": "reservation",
        "gpus_per_node": "gpus_per_node",
        "gpus_per_task": "gpus_per_task",
    }

    for opt_key, config_key in direct_mappings.items():
        if opt_key in options and options[opt_key] is not None:
            setattr(config, config_key, options[opt_key])

    # Handle GPU options
    if "gpus" in options:
        _parse_gpu_option(options["gpus"], config)
    elif "gres" in options:
        _parse_gres_option(options["gres"], config)

    return config


def _parse_sbatch_directive(line: str, config: SlurmConfig) -> None:
    """Parse a single #SBATCH directive line.

    Args:
        line: SBATCH directive line
        config: Config object to update
    """
    # Remove #SBATCH prefix
    directive = line.replace("#SBATCH", "").strip()

    # Store raw directive
    config.raw_directives[line] = directive

    # Parse common formats: --option=value, --option value, -o value
    if "=" in directive:
        # Format: --option=value
        parts = directive.split("=", 1)
        option = parts[0].strip().lstrip("-")
        value = parts[1].strip()
    else:
        # Format: --option value or -o value
        parts = directive.split(None, 1)
        if len(parts) < 2:
            return
        option = parts[0].strip().lstrip("-")
        value = parts[1].strip() if len(parts) > 1 else ""

    # Map to config attributes
    _map_slurm_option(option, value, config)


def _map_slurm_option(option: str, value: str, config: SlurmConfig) -> None:
    """Map SLURM option to config attribute.

    Args:
        option: Option name (without dashes)
        value: Option value
        config: Config object to update
    """
    # Store original option for single-letter options
    original_option = option

    # Normalize option name (but preserve case sensitivity for single letters)
    if len(option) > 1:
        option = option.lower().replace("-", "_")

    # Handle different option names
    if option in ["j", "J", "job_name"]:
        config.job_name = value
    elif option in ["p", "P", "partition"]:
        config.partition = value
    elif option in ["N", "nodes"]:
        config.nodes = int(value)
    elif option in ["n", "ntasks"]:
        config.ntasks = int(value)
    elif option in ["c", "cpus_per_task"]:
        config.cpus_per_task = int(value)
    elif option == "mem":
        config.mem = value
    elif option == "mem_per_cpu":
        config.mem_per_cpu = value
    elif option == "mem_per_gpu":
        config.mem_per_gpu = value
    elif option in ["t", "T", "time"]:
        config.time = value
    elif option in ["G", "gpus"]:
        _parse_gpu_option(value, config)
    elif option == "gres":
        _parse_gres_option(value, config)
    elif option in ["C", "constraint"]:
        config.constraint = value
    elif option in ["a", "array"]:
        config.array = value
    elif option in ["d", "dependency"]:
        config.dependency = value
    elif option in ["qos"]:
        config.qos = value
    elif option in ["A", "account"]:
        # Note: upper-case -A is account in SLURM; handled here as well
        config.account = value
    elif option in ["reservation"]:
        config.reservation = value
    elif option in ["o", "output"]:
        config.output = value
    elif option in ["e", "error"]:
        config.error = value
    elif option == "mail_type":
        config.mail_type = value
    elif option == "mail_user":
        config.mail_user = value
    elif option in ["D", "chdir"]:
        config.working_directory = value
    elif option == "export":
        # Handle environment export
        if value.upper() != "NONE":
            _parse_export_option(value, config)
    elif option in ["ntasks_per_node"]:
        try:
            config.ntasks_per_node = int(value)
        except Exception:
            logger.warning(f"Invalid ntasks_per_node value: {value}")
    elif option in ["gpus_per_node"]:
        _parse_gpus_per_node_option(value, config)
    elif option in ["gpus_per_task"]:
        try:
            # Support both formats: "4" and "a100:4" (type ignored for per-task)
            if ":" in value:
                _, count = value.split(":", 1)
                config.gpus_per_task = int(count)
            else:
                config.gpus_per_task = int(value)
        except Exception:
            logger.warning(f"Invalid gpus_per_task value: {value}")


def _parse_gpu_option(gpu_spec: str, config: SlurmConfig) -> None:
    """Parse GPU specification (e.g., '1', 'a100:2').

    Args:
        gpu_spec: GPU specification string
        config: Config object to update
    """
    if ":" in gpu_spec:
        # Format: gpu_type:count
        gpu_type, count = gpu_spec.split(":", 1)
        config.instance_type = gpu_type
        config.gpus = int(count)
    else:
        # Just count
        config.gpus = int(gpu_spec)


def _parse_gres_option(gres_spec: str, config: SlurmConfig) -> None:
    """Parse GRES specification (e.g., 'gpu:1', 'gpu:v100:2').

    Args:
        gres_spec: GRES specification string
        config: Config object to update
    """
    if not gres_spec.startswith("gpu"):
        return  # Only handle GPU GRES for now

    parts = gres_spec.split(":")
    if len(parts) == 2:
        # Format: gpu:count
        config.gpus = int(parts[1])
    elif len(parts) == 3:
        # Format: gpu:type:count
        config.instance_type = parts[1]
        config.gpus = int(parts[2])


def _parse_gpus_per_node_option(spec: str, config: SlurmConfig) -> None:
    """Parse gpus-per-node specification (e.g., '4', 'a100:4').

    Args:
        spec: GPUs per node specification
        config: Config object to update
    """
    try:
        if ":" in spec:
            gpu_type, count = spec.split(":", 1)
            config.instance_type = gpu_type
            config.gpus_per_node = int(count)
        else:
            config.gpus_per_node = int(spec)
    except Exception:
        logger.warning(f"Invalid gpus-per-node spec: {spec}")


def _parse_export_option(export_spec: str, config: SlurmConfig) -> None:
    """Parse environment export specification.

    Args:
        export_spec: Export specification (e.g., 'ALL', 'VAR=value')
        config: Config object to update
    """
    if export_spec.upper() == "ALL":
        # Export all current environment variables
        import os

        config.environment.update(os.environ)
    elif "=" in export_spec:
        # Specific variable assignment
        for var_assignment in export_spec.split(","):
            if "=" in var_assignment:
                key, value = var_assignment.split("=", 1)
                config.environment[key.strip()] = value.strip()


def parse_time_to_hours(time_str: str) -> float:
    """Convert SLURM time format to hours.

    Supported formats:
    - MM:SS
    - HH:MM:SS
    - DD-HH:MM:SS
    - DD-HH

    Args:
        time_str: Time string in SLURM format

    Returns:
        Time in hours as float
    """
    if "-" in time_str:
        # Format: DD-HH:MM:SS or DD-HH
        parts = time_str.split("-", 1)
        days = int(parts[0])

        if ":" in parts[1]:
            time_parts = parts[1].split(":")
            hours = int(time_parts[0]) if time_parts[0] else 0
            minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
            seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
        else:
            hours = int(parts[1])
            minutes = 0
            seconds = 0

        total_hours = days * 24 + hours + minutes / 60 + seconds / 3600
    else:
        # Format: HH:MM:SS or MM:SS
        time_parts = time_str.split(":")

        if len(time_parts) == 3:
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            seconds = int(time_parts[2])
        elif len(time_parts) == 2:
            hours = 0
            minutes = int(time_parts[0])
            seconds = int(time_parts[1])
        else:
            # Just minutes
            hours = 0
            minutes = int(time_str)
            seconds = 0

        total_hours = hours + minutes / 60 + seconds / 3600

    return total_hours


def parse_memory_to_gb(mem_str: str) -> float:
    """Convert SLURM memory format to GB.

    Supported formats:
    - 1024 (assumed MB)
    - 1024M or 1024MB
    - 16G or 16GB
    - 1T or 1TB

    Args:
        mem_str: Memory string in SLURM format

    Returns:
        Memory in GB as float
    """
    mem_str = mem_str.strip().upper()

    # Extract numeric part and unit
    match = re.match(r"^(\d+(?:\.\d+)?)\s*([MGTP]?B?)$", mem_str)
    if not match:
        raise ValueError(f"Invalid memory format: {mem_str}")

    value = float(match.group(1))
    unit = match.group(2)

    # Convert to GB
    if unit in ["", "M", "MB"]:
        # Megabytes (default if no unit)
        return value / 1024
    elif unit in ["G", "GB"]:
        # Gigabytes
        return value
    elif unit in ["T", "TB"]:
        # Terabytes
        return value * 1024
    elif unit in ["P", "PB"]:
        # Petabytes
        return value * 1024 * 1024
    else:
        raise ValueError(f"Unknown memory unit: {unit}")
