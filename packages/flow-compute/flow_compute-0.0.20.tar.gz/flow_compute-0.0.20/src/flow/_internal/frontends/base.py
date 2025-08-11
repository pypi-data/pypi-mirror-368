"""Base frontend adapter for Flow SDK."""

import logging
from abc import ABC, abstractmethod
from typing import Any

from flow.api.models import TaskConfig

logger = logging.getLogger(__name__)


class BaseFrontendAdapter(ABC):
    """Base class for frontend adapters.

    Frontend adapters are responsible for:
    1. Parsing user input in various formats (SLURM, Submitit, etc.)
    2. Converting to the common TaskConfig intermediate representation
    3. Providing compatibility features (environment variables, output formats)
    """

    def __init__(self, name: str):
        self.name = name
        logger.info(f"Initialized {name} frontend adapter")

    @abstractmethod
    async def parse_and_convert(self, input_data: Any, **options: Any) -> TaskConfig:
        """Parse input and convert to TaskConfig.

        Args:
            input_data: Frontend-specific input (script path, function, etc.)
            **options: Additional frontend-specific options

        Returns:
            Common TaskConfig intermediate representation
        """
        pass

    def to_flow_task_config(self, task_config: TaskConfig) -> TaskConfig:
        """Pass through TaskConfig (no conversion needed).

        Args:
            task_config: Common TaskConfig

        Returns:
            Same TaskConfig for submission
        """
        # Since we're using a unified TaskConfig model, just return it
        return task_config

    @abstractmethod
    def format_job_id(self, flow_job_id: str) -> str:
        """Format Flow job ID for frontend display.

        Args:
            flow_job_id: Internal Flow job ID

        Returns:
            Frontend-specific job ID format
        """
        pass

    @abstractmethod
    def format_status(self, flow_status: str) -> str:
        """Format Flow status for frontend display.

        Args:
            flow_status: Internal Flow status

        Returns:
            Frontend-specific status format
        """
        pass
