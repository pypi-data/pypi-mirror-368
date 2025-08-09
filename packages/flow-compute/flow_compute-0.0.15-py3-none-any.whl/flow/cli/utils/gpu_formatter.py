"""GPU and instance type formatting utilities for CLI output."""

import re
from typing import Optional


class GPUFormatter:
    """Handles GPU and instance type formatting.

    This formatter provides consistent GPU information display across all CLI commands,
    handling various instance type formats and providing compact representations
    for narrow terminal displays.
    """

    @staticmethod
    def format_gpu_type(instance_type: Optional[str]) -> str:
        """Extract and format GPU type from instance type string.

        Args:
            instance_type: Raw instance type string from API

        Returns:
            Formatted GPU type string or "N/A" if not available
        """
        if not instance_type:
            return "N/A"

        # If it's an opaque ID (starts with it_), show truncated version
        if instance_type.startswith("it_"):
            return instance_type[:12].upper() + "..."

        # Otherwise just format what we have
        return instance_type.upper()

    @staticmethod
    def format_compact_gpu(gpu_type: str, max_width: int = 10) -> str:
        """Format GPU type for narrow displays.

        Args:
            gpu_type: GPU type string to format
            max_width: Maximum width for the output

        Returns:
            Compact GPU representation
        """
        if not gpu_type or gpu_type == "N/A":
            return "-"

        # Extract key GPU info (e.g., "4xa100" -> "4xA100")
        match = re.search(r"(\d+)x([a-z]+\d+)", gpu_type.lower())
        if match:
            count, model = match.groups()
            return f"{count}x{model.upper()}"

        # For IDs, show first 8 chars
        if gpu_type.startswith(("IT_", "it_")):
            return gpu_type[:8]

        # Truncate if needed
        if len(gpu_type) > max_width:
            return gpu_type[:max_width]

        return gpu_type

    @staticmethod
    def parse_gpu_count(instance_type: str) -> int:
        """Extract GPU count from instance type string.

        Args:
            instance_type: Instance type string

        Returns:
            Number of GPUs, or 0 if not found
        """
        if not instance_type:
            return 0

        # Look for patterns like "4xa100" or "8xh100"
        match = re.search(r"(\d+)x[a-z]+\d+", instance_type.lower())
        if match:
            return int(match.group(1))

        # Single GPU patterns
        if re.search(r"[a-z]+\d+", instance_type.lower()):
            return 1

        return 0

    @staticmethod
    def intelligent_gpu_truncate(gpu_name: str, max_width: int) -> str:
        """Intelligently truncate GPU names while preserving important information.

        This method extracts and prioritizes the most important parts of GPU names:
        1. GPU model (A100, H100, V100, etc.)
        2. Memory size (80GB, 40GB, etc.)
        3. Count/quantity (4x, 8x)

        Args:
            gpu_name: Full GPU name string
            max_width: Maximum display width

        Returns:
            Intelligently truncated GPU string
        """
        if len(gpu_name) <= max_width:
            return gpu_name

        # If it's an opaque ID, truncate from start
        if gpu_name.startswith(("IT_", "it_")):
            return gpu_name[: max_width - 3] + "..."

        # Extract key components using various patterns
        components = []

        # Look for GPU count (e.g., 4x, 8x)
        count_match = re.search(r"(\d+)[xX]", gpu_name)
        if count_match:
            components.append(count_match.group(0))

        # Look for GPU models (common patterns)
        model_patterns = [
            r"[AHV]\d{2,3}",  # A100, H100, V100
            r"RTX\s*\d{4}",  # RTX 3090, RTX 4090
            r"T4",  # T4
            r"P\d{2,3}",  # P100, P40
            r"K\d{2}",  # K80
            r"M\d{2}",  # M60
        ]

        for pattern in model_patterns:
            model_match = re.search(pattern, gpu_name, re.IGNORECASE)
            if model_match:
                model = model_match.group(0).upper()
                if model not in " ".join(components):
                    components.append(model)
                break

        # Look for memory size (e.g., 80GB, 40GB)
        mem_match = re.search(r"(\d{1,3})\s*GB", gpu_name, re.IGNORECASE)
        if mem_match:
            mem_size = f"{mem_match.group(1)}GB"
            if mem_size not in " ".join(components):
                components.append(mem_size)

        # If we found components, build a compact representation
        if components:
            result = " ".join(components)
            if len(result) <= max_width:
                return result
            # If still too long, prioritize model and memory
            if len(components) > 2:
                result = " ".join(components[:2])
                if len(result) <= max_width:
                    return result

        # Fallback: extract most important substring
        # Try to find and preserve GPU model names
        for pattern in model_patterns:
            match = re.search(pattern, gpu_name, re.IGNORECASE)
            if match:
                model = match.group(0).upper()
                # Try to include memory if possible
                remaining = max_width - len(model) - 1
                if remaining > 4:  # Space for "40GB"
                    mem_match = re.search(r"(\d{1,3})\s*GB", gpu_name, re.IGNORECASE)
                    if mem_match:
                        return f"{model} {mem_match.group(1)}GB"[:max_width]
                return model

        # Last resort: middle truncation
        if max_width > 6:
            start = (max_width - 3) // 2
            end = max_width - 3 - start
            return gpu_name[:start] + "..." + gpu_name[-end:]
        else:
            return gpu_name[:max_width]

    @staticmethod
    def format_gpu_details(instance_type: str, num_instances: int = 1) -> str:
        """Format detailed GPU information including total GPU count.

        Args:
            instance_type: Instance type string
            num_instances: Number of instances

        Returns:
            Detailed GPU information string
        """
        gpu_per_instance = GPUFormatter.parse_gpu_count(instance_type)
        total_gpus = gpu_per_instance * num_instances

        if total_gpus == 0:
            return "No GPUs"

        gpu_type = GPUFormatter.format_gpu_type(instance_type)

        if num_instances == 1:
            return gpu_type
        else:
            # For details view, show full breakdown
            # Extract just the model name from the gpu_type
            import re

            model_match = re.search(
                r"[AHV]\d{2,3}|RTX\s*\d{4}|T4|[PK]\d{2,3}|M\d{2}", gpu_type, re.IGNORECASE
            )
            if model_match:
                model = model_match.group(0).upper()
            else:
                # Fallback: try to clean up the type string
                model = gpu_type.replace("×", "").replace("X", "")
                # Remove leading digits
                model = re.sub(r"^\d+", "", model)

            # Example: "16×H100 (2 nodes × 8 GPUs each)"
            return f"{total_gpus}×{model} ({num_instances} nodes × {gpu_per_instance} GPUs each)"

    @staticmethod
    def format_ultra_compact(instance_type: str, num_instances: int = 1) -> str:
        """Format GPU info in ultra-compact form for table display.

        Examples:
            Single node:
                "8x h100 80gb" -> "8×H100·80G"
                "4xa100" -> "4×A100"
                "a100-80gb" -> "A100·80G"
                "h100" -> "H100"

            Multi-node (shows total GPUs first):
                "8xh100", num_instances=4 -> "32×H100 (4×8)"
                "h100", num_instances=8 -> "8×H100 (8×1)"
                "4xa100", num_instances=2 -> "8×A100 (2×4)"

        Args:
            instance_type: Instance type string
            num_instances: Number of instances (nodes)

        Returns:
            Ultra-compact GPU representation:
            - Single node: GPUs×Model·Memory
            - Multi-node: TotalGPUs×Model (Nodes×GPUsPerNode)
        """
        if not instance_type:
            return "-"

        # Handle opaque IDs
        if instance_type.lower().startswith("it_"):
            # For opaque IDs, keep old format since we can't extract GPU count
            base = instance_type[:8].upper()
            if num_instances > 1:
                return f"{base}×{num_instances}"
            return base

        # Normalize the string
        normalized = instance_type.lower().replace(" ", "").replace("-", "")

        # Extract components
        gpus_per_node = 1  # Default to 1 GPU per node
        model = ""
        memory = ""

        # Match patterns like "8xa100" or "4xh100"
        count_model_match = re.match(r"(\d+)x([ahvtp]\d{2,3})", normalized)
        if count_model_match:
            gpus_per_node = int(count_model_match.group(1))
            model = count_model_match.group(2).upper()
            # Check for memory after model
            rest = normalized[count_model_match.end() :]
            mem_match = re.search(r"(\d{2,3})gb?", rest)
            if mem_match:
                memory = mem_match.group(1).lstrip("0") + "G"
        else:
            # Try to find just model
            model_match = re.search(r"([ahvtp]\d{2,3}|rtx\d{4})", normalized)
            if model_match:
                model = model_match.group(1).upper()
                # Check for memory AFTER the model to avoid matching digits in model name
                search_start = model_match.end()
                mem_match = re.search(r"(\d{2,3})gb?", normalized[search_start:])
                if mem_match:
                    memory = mem_match.group(1).lstrip("0") + "G"

        # If we couldn't parse a model, use truncated instance type
        if not model:
            model = instance_type.upper()[:6]

        # Calculate total GPUs
        total_gpus = gpus_per_node * num_instances

        # Build the representation based on single vs multi-node
        if num_instances == 1:
            # Single node: use original compact format
            parts = []
            if gpus_per_node > 1:
                parts.append(f"{gpus_per_node}×{model}")
            else:
                parts.append(model)

            if memory:
                parts.append(f"·{memory}")

            return "".join(parts)
        else:
            # Multi-node: show total GPUs (clean, no breakdown in table view)
            base = f"{total_gpus}×{model}"

            # Add memory if present
            if memory:
                base += f"·{memory}"

            return base

    @staticmethod
    def format_ultra_compact_width_aware(
        instance_type: str, num_instances: int = 1, max_width: Optional[int] = None
    ) -> str:
        """Format GPU info with width constraints for responsive display.

        This method gracefully degrades the display format based on available width:
        - Full: "32×H100·80G (4×8)"
        - Medium: "32×H100 (4×8)"
        - Narrow: "32×H100"
        - Ultra-narrow: "32×H100" truncated

        Args:
            instance_type: Instance type string
            num_instances: Number of instances (nodes)
            max_width: Maximum display width (None = no limit)

        Returns:
            Width-appropriate GPU representation
        """
        # Get the full format first
        full_format = GPUFormatter.format_ultra_compact(instance_type, num_instances)

        # If no width constraint or fits, return full format
        if max_width is None or len(full_format) <= max_width:
            return full_format

        # For single node, use intelligent truncation
        if num_instances == 1:
            return GPUFormatter.intelligent_gpu_truncate(full_format, max_width)

        # For multi-node, progressively simplify
        # Try without memory first if needed
        if "·" in full_format and len(full_format) > max_width:
            base_no_mem = full_format.split("·")[0]
            if len(base_no_mem) <= max_width:
                return base_no_mem

        # Last resort: truncate
        if max_width > 3:
            return full_format[: max_width - 3] + "..."
        else:
            return full_format[:max_width]
