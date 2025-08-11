"""Centralized utilities for masking sensitive values."""

from typing import Any, TYPE_CHECKING

# Avoid runtime import cycles while preserving type hints
if TYPE_CHECKING:  # Only for type checkers; not executed at runtime
    from flow.core.setup_adapters import ConfigField as ConfigFieldType
else:
    ConfigFieldType = Any


def mask_sensitive_value(
    value: str | None, head: int = 8, tail: int = 4, min_length: int = 10
) -> str:
    """Mask a sensitive value for display.

    Args:
        value: The value to mask
        head: Number of characters to show at the beginning
        tail: Number of characters to show at the end
        min_length: Minimum length before masking (shorter values are fully masked)

    Returns:
        Masked value suitable for display

    Examples:
        >>> mask_sensitive_value("sk_live_abcd1234efgh5678")
        'sk_live_...5678'
        >>> mask_sensitive_value("short")
        '[CONFIGURED]'
        >>> mask_sensitive_value(None)
        '[NOT SET]'
    """
    if not value:
        return "[NOT SET]"

    if len(value) <= min_length:
        return "[CONFIGURED]"

    return f"{value[:head]}...{value[-tail:]}"


def mask_strict_last4(value: str | None, min_length: int = 10) -> str:
    """Strict masking that reveals only the last 4 characters.

    Displays as "••••xxxx" when value is sufficiently long; otherwise shows
    a generic placeholder without leaking characters.

    Args:
        value: The string to mask
        min_length: Minimum length before revealing last 4; shorter values
            are fully concealed with "[CONFIGURED]".

    Returns:
        Strictly masked value suitable for display

    Examples:
        >>> mask_strict_last4("sk_live_abcd1234efgh5678")
        '••••5678'
        >>> mask_strict_last4("short")
        '[CONFIGURED]'
        >>> mask_strict_last4(None)
        '[NOT SET]'
    """
    if not value:
        return "[NOT SET]"

    if len(value) <= min_length:
        return "[CONFIGURED]"

    return f"••••{value[-4:]}"


def mask_api_key(api_key: str | None) -> str:
    """Mask an API key for safe display using strict last-4 style.

    Args:
        api_key: The API key to mask

    Returns:
        Masked API key like "••••wxyz"
    """
    return mask_strict_last4(api_key)


def mask_ssh_key_fingerprint(fingerprint: str | None) -> str:
    """Mask an SSH key fingerprint for display.

    SSH fingerprints are less sensitive but we still truncate for consistency.

    Args:
        fingerprint: The SSH key fingerprint

    Returns:
        Masked fingerprint
    """
    return mask_sensitive_value(fingerprint, head=12, tail=8, min_length=20)


def mask_config_for_display(config: dict[str, Any], fields: list[ConfigFieldType]) -> dict[str, Any]:
    """Return a masked copy of a configuration dict for safe display.

    Any field that is marked with mask_display in the provided field specs
    will be masked using mask_sensitive_value if the value is a string.

    Args:
        config: The configuration mapping to mask
        fields: Field specifications that describe which keys are sensitive

    Returns:
        A shallow copy of the config with sensitive fields masked
    """
    masked: dict[str, Any] = dict(config)
    try:
        field_map = {getattr(f, "name", None): f for f in fields}
    except Exception:
        field_map = {}

    for key, value in list(config.items()):
        field = field_map.get(key)
        if field and getattr(field, "mask_display", False) and isinstance(value, str):
            # Use strict last-4 style for any field marked as sensitive
            masked[key] = mask_strict_last4(value)

    return masked
