"""Simple HTTP client for Flow SDK."""

import logging
import threading
import time
from typing import Any, Dict, Optional, Tuple
from weakref import WeakValueDictionary

import httpx

from flow.errors import APIError, AuthenticationError, NetworkError, TimeoutError

logger = logging.getLogger(__name__)


class HttpClient:
    """Basic HTTP client with auto JSON handling."""

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """Initialize HTTP client.

        Args:
            base_url: Base URL for all requests
            headers: Default headers to include in all requests
        """
        # Store base_url as attribute for access by consumers
        self.base_url = base_url

        # Configure transport with built-in retries for connection errors
        transport = httpx.HTTPTransport(
            retries=3,  # Retry connection errors automatically
        )

        self.client = httpx.Client(
            base_url=base_url,
            headers=headers or {},
            timeout=httpx.Timeout(30.0),
            transport=transport,
            follow_redirects=True,  # Follow redirects automatically
        )

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
        params: Optional[Dict[str, str]] = None,
        retry_server_errors: bool = True,
    ) -> Dict[str, Any]:
        """Make HTTP request and return JSON response.

        Transport layer handles connection retries automatically.
        This method only retries 5xx server errors if enabled.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL path (relative to base_url)
            headers: Additional headers for this request
            json: JSON body to send
            params: Query parameters
            retry_server_errors: Whether to retry 5xx errors (default: True)

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: For 401/403 responses
            ValidationAPIError: For 422 validation errors with details
            APIError: For other API errors
            TimeoutError: For request timeouts
            NetworkError: For connection errors
        """
        max_retries = 3 if retry_server_errors else 1
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    params=params,
                )
                response.raise_for_status()

                # Handle 204 No Content response (e.g., from DELETE operations)
                if response.status_code == 204:
                    return {}

                # Parse JSON response
                return response.json()

            except httpx.HTTPStatusError as e:
                # Convert to specific errors
                if e.response.status_code == 401:
                    raise AuthenticationError(
                        "Invalid API key. Run 'flow init' to configure authentication."
                    ) from e
                elif e.response.status_code == 403:
                    raise AuthenticationError(
                        "Access denied. Check your API key permissions."
                    ) from e
                elif e.response.status_code == 404:
                    # Pass through the actual error message from the API
                    raise APIError(f"Not found: {e.response.text}") from e
                elif e.response.status_code == 422:
                    # Validation error - parse and format the details
                    from flow.errors import ValidationAPIError

                    raise ValidationAPIError(e.response) from e
                elif e.response.status_code == 504:
                    # Gateway timeout
                    raise TimeoutError(f"Gateway timeout: {e.response.text}") from e
                elif e.response.status_code >= 500:
                    # Server error - maybe retry
                    if attempt < max_retries - 1:
                        delay = min(2**attempt, 10)
                        logger.warning(
                            f"Server error {e.response.status_code} (attempt {attempt + 1}/{max_retries}), "
                            f"retrying in {delay}s"
                        )
                        time.sleep(delay)
                        continue
                    last_error = APIError(
                        f"Server error {e.response.status_code}: {e.response.text}"
                    )
                else:
                    # Other client errors - don't retry
                    error_text = e.response.text
                    # Add helpful message for quota errors
                    if "quota" in error_text.lower():
                        error_text += "\nCheck quota: https://app.mithril.ai/instances/quotas"
                    # Add helpful message for name conflicts
                    elif (
                        e.response.status_code == 400 and "name already used" in error_text.lower()
                    ):
                        error_text += "\n\nHint: Add 'unique_name: true' to your config to automatically generate unique names."
                    raise APIError(f"API error {e.response.status_code}: {error_text}") from e

            except httpx.TimeoutException as e:
                raise TimeoutError(f"Request timed out: {url}") from e

            except httpx.RequestError as e:
                # Connection errors are already retried by transport
                raise NetworkError(f"Network error: {e}") from e

        raise last_error

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        _ = (exc_type, exc_val, exc_tb)  # Unused but required by protocol
        self.close()


class HttpClientPool:
    """Singleton pool for HTTP clients to enable connection reuse.

    This pool maintains HTTP clients keyed by their base URL and headers,
    allowing multiple Flow instances to share the same underlying connections.
    Uses weak references to allow garbage collection when clients are no longer needed.
    """

    _clients: WeakValueDictionary[Tuple, HttpClient] = WeakValueDictionary()
    _lock = threading.Lock()

    @classmethod
    def get_client(cls, base_url: str, headers: Optional[Dict[str, str]] = None) -> HttpClient:
        """Get or create a pooled HTTP client.

        Args:
            base_url: Base URL for the client
            headers: Default headers for the client

        Returns:
            Shared HttpClient instance
        """
        # Create a hashable key from base_url and headers
        headers = headers or {}
        key = (base_url, tuple(sorted(headers.items())))

        # Fast path - no lock needed for reads
        client = cls._clients.get(key)
        if client is not None:
            return client

        # Slow path - create new client outside lock
        new_client = HttpClient(base_url, headers)

        # Only lock for the minimal critical section
        with cls._lock:
            # Race condition check - another thread might have created it
            existing = cls._clients.get(key)
            if existing is not None:
                # Discard our client and use the existing one
                new_client.close()
                return existing

            # We won the race, store our client
            cls._clients[key] = new_client
            logger.debug(f"Created new HTTP client for {base_url}")
            return new_client

    @classmethod
    def clear_pool(cls) -> None:
        """Clear all pooled clients. Useful for testing."""
        cls._clients.clear()
