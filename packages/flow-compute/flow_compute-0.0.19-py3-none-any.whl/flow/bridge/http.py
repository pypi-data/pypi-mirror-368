"""HTTP client bridge adapter."""

import json
from typing import Any, Dict, Optional

from flow._internal.io.http import HttpClient
from flow.errors import APIError, AuthenticationError, NetworkError, TimeoutError

from .base import BridgeAdapter


class HTTPBridge(BridgeAdapter):
    """Bridge adapter for Flow SDK HTTP client."""

    def __init__(self):
        """Initialize the HTTP bridge."""
        self._clients = {}  # Cache clients by base URL

    def get_capabilities(self) -> Dict[str, Any]:
        """Return capabilities of the HTTP adapter."""
        return {
            "description": "HTTP client with retry logic and error handling",
            "methods": {
                "request": {
                    "description": "Make HTTP request with JSON response",
                    "args": {
                        "base_url": "Base URL for the request",
                        "method": "HTTP method (GET, POST, etc.)",
                        "path": "URL path relative to base URL",
                        "headers": "Additional headers (optional)",
                        "json": "JSON body (optional)",
                        "params": "Query parameters (optional)",
                    },
                    "returns": "dict (JSON response)",
                },
                "close_client": {
                    "description": "Close HTTP client for a base URL",
                    "args": {"base_url": "Base URL of client to close"},
                    "returns": "bool",
                },
            },
        }

    def request(
        self,
        base_url: str,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request and return JSON response.

        Args:
            base_url: Base URL for the request
            method: HTTP method (GET, POST, etc.)
            path: URL path relative to base URL
            headers: Additional headers
            json: JSON body to send
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            Various Flow SDK errors that will be serialized by bridge
        """
        # Get or create client for this base URL
        if base_url not in self._clients:
            # Default headers that mithril-js would set
            default_headers = {
                "Content-Type": "application/json",
            }
            if headers:
                default_headers.update(headers)

            self._clients[base_url] = HttpClient(base_url, default_headers)

        client = self._clients[base_url]

        # Make request - errors will be caught by bridge framework
        response = client.request(
            method=method,
            url=path,
            headers=headers,
            json=json,
            params=params,
        )

        # Ensure response is JSON-serializable
        return self._ensure_serializable(response)

    def close_client(self, base_url: str) -> bool:
        """Close HTTP client for a base URL.

        Args:
            base_url: Base URL of client to close

        Returns:
            True if client was closed, False if not found
        """
        if base_url in self._clients:
            self._clients[base_url].close()
            del self._clients[base_url]
            return True
        return False

    def _ensure_serializable(self, obj: Any) -> Any:
        """Ensure object is JSON-serializable.

        Args:
            obj: Object to check/convert

        Returns:
            JSON-serializable version of object
        """
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, dict):
            return {k: self._ensure_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._ensure_serializable(v) for v in obj]
        else:
            # Convert to string for unknown types
            return str(obj)
