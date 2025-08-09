"""Centralized utilities for masking sensitive values."""

from typing import Optional, Dict, Any, List

# Importing here avoids cycles because adapters do not import this module
try:
    from flow.core.setup_adapters import ConfigField
except Exception:  # Fallback typing-only import safety
    ConfigField = object  # type: ignore


def mask_sensitive_value(value: Optional[str], head: int = 8, tail: int = 4, min_length: int = 10) -> str:
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


def mask_api_key(api_key: Optional[str]) -> str:
    """Mask an API key for safe display.
    
    Standard masking for API keys, showing first 8 and last 4 characters.
    
    Args:
        api_key: The API key to mask
    
    Returns:
        Masked API key
    """
    return mask_sensitive_value(api_key, head=8, tail=4)


def mask_ssh_key_fingerprint(fingerprint: Optional[str]) -> str:
    """Mask an SSH key fingerprint for display.
    
    SSH fingerprints are less sensitive but we still truncate for consistency.
    
    Args:
        fingerprint: The SSH key fingerprint
    
    Returns:
        Masked fingerprint
    """
    return mask_sensitive_value(fingerprint, head=12, tail=8, min_length=20)


def mask_config_for_display(config: Dict[str, Any], fields: List[ConfigField]) -> Dict[str, Any]:
    """Return a masked copy of a configuration dict for safe display.

    Any field that is marked with mask_display in the provided field specs
    will be masked using mask_sensitive_value if the value is a string.

    Args:
        config: The configuration mapping to mask
        fields: Field specifications that describe which keys are sensitive

    Returns:
        A shallow copy of the config with sensitive fields masked
    """
    masked: Dict[str, Any] = dict(config)
    try:
        field_map = {getattr(f, "name", None): f for f in fields}
    except Exception:
        field_map = {}

    for key, value in list(config.items()):
        field = field_map.get(key)
        if field and getattr(field, "mask_display", False) and isinstance(value, str):
            masked[key] = mask_sensitive_value(value)

    return masked