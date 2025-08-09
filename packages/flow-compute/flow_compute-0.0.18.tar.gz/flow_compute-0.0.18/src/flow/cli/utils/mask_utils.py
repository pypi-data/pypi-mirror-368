"""Centralized utilities for masking sensitive values."""

from typing import Optional


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