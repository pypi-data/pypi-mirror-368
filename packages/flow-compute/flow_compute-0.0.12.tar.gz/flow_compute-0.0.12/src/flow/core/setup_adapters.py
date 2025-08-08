"""Setup adapter interfaces for Flow SDK.

This module defines the adapter pattern that allows the GenericSetupWizard
to work with any provider while maintaining its beautiful UI and functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum


class FieldType(Enum):
    """Types of configuration fields."""

    TEXT = "text"
    PASSWORD = "password"
    CHOICE = "choice"
    BOOLEAN = "boolean"


@dataclass
class ConfigField:
    """Configuration field specification."""

    name: str
    field_type: FieldType
    required: bool = True
    mask_display: bool = False  # For API keys, etc.
    help_url: Optional[str] = None
    help_text: Optional[str] = None
    default: Optional[str] = None
    choices: Optional[List[str]] = None  # For CHOICE type
    dynamic_choices: bool = False  # If choices come from API
    display_name: Optional[str] = None  # Custom display name in UI


@dataclass
class ValidationResult:
    """Result of field validation."""

    is_valid: bool
    message: Optional[str] = None
    display_value: Optional[str] = None  # For masked fields
    processed_value: Optional[str] = None  # For transformations like SSH key generation


class ProviderSetupAdapter(ABC):
    """Adapter interface for provider-specific setup logic.

    This allows the GenericSetupWizard to work with any provider
    while maintaining its polished UI and functionality.
    """

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass

    @abstractmethod
    def get_configuration_fields(self) -> List[ConfigField]:
        """Get the configuration fields for this provider."""
        pass

    @abstractmethod
    def validate_field(
        self, field_name: str, value: str, context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate a single field value.

        Args:
            field_name: Name of the field
            value: Field value to validate
            context: Optional context with previously configured values

        Returns:
            ValidationResult with validation status and display value
        """
        pass

    @abstractmethod
    def get_dynamic_choices(self, field_name: str, context: Dict[str, Any]) -> List[str]:
        """Get dynamic choices for a field (e.g., projects from API).

        Args:
            field_name: Name of the field
            context: Previously configured values for context

        Returns:
            List of available choices
        """
        pass

    @abstractmethod
    def detect_existing_config(self) -> Dict[str, Any]:
        """Detect existing configuration from environment, files, etc.

        Returns:
            Dictionary of detected configuration values
        """
        pass

    @abstractmethod
    def save_configuration(self, config: Dict[str, Any]) -> bool:
        """Save the final configuration.

        Args:
            config: Configuration to save

        Returns:
            True if save was successful
        """
        pass

    @abstractmethod
    def verify_configuration(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Verify that the configuration works end-to-end.

        Args:
            config: Configuration to verify

        Returns:
            Tuple of (success, error_message)
        """
        pass

    def get_welcome_message(self) -> Tuple[str, List[str]]:
        """Get provider-specific welcome message.

        Returns:
            Tuple of (title, feature_list)
        """
        return (
            f"{self.get_provider_name().upper()} Provider Setup",
            ["Configure authentication", "Select project settings", "Set up optional features"],
        )

    def get_completion_message(self) -> str:
        """Get provider-specific completion message."""
        return f"Your {self.get_provider_name().upper()} configuration is ready!"
