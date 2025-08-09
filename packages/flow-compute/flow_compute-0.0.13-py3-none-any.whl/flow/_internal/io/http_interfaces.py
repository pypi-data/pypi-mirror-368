"""HTTP client abstraction for provider communication.

This module defines the HTTP interface enabling different implementations
(requests, httpx, aiohttp) while maintaining consistent behavior.
"""

from typing import Any, Dict, Optional, Protocol


class IHttpClient(Protocol):
    """HTTP client abstraction for provider communication.

    Defines a minimal HTTP interface enabling different implementations
    (requests, httpx, aiohttp) while maintaining consistent behavior.
    Implementations must handle authentication, retries, and connection
    pooling transparently.

    Implementations must provide:
      - Automatic retry with exponential backoff for transient failures
      - Connection pooling for performance (100+ connections)
      - Request/response logging for debugging (debug level)
      - Timeout handling (30s default, configurable)
      - Error mapping to FlowError hierarchy
      - Thread-safe operation for concurrent requests
    """

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP request with automatic retries.

        Performs HTTP request with built-in retry logic, connection pooling,
        and comprehensive error handling. All network failures are mapped to
        appropriate FlowError subclasses. Retries 3 times with exponential
        backoff (1s, 2s, 4s with jitter) for 5xx errors, connection errors,
        and timeouts. Does not retry 4xx client errors.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH). Case-insensitive.
            url: URL path relative to base URL. Leading slash optional.
                Example: "spot/bids" or "/spot/bids".
            headers: Additional HTTP headers. Base headers (auth, user-agent)
                are added automatically.
            json: Request body for POST/PUT/PATCH. Automatically serialized.
            params: URL query parameters. Values converted to strings. None
                values omitted. Lists become repeated params.

        Returns:
            Parsed JSON response body. Empty dict for 204.

        Raises:
            ValidationError: 400 Bad Request with field-level errors.
            AuthenticationError: 401 Unauthorized (invalid API key).
            ResourceNotFoundError: 404 Not Found.
            ValidationAPIError: 422 Unprocessable Entity with details.
            APIError: Other 4xx/5xx errors with status code.
            NetworkError: Connection failures, DNS errors.
            TimeoutError: Request exceeded timeout (30s default).
        """
        ...

    def close(self) -> None:
        """Release HTTP client resources gracefully.

        Closes connection pools, cancels pending requests, and frees resources.
        Safe to call multiple times. Should be called on application shutdown
        or provider cleanup. Implementations should close all connection pools,
        cancel in-flight requests (best effort), clear authentication tokens,
        flush logs and metrics, and not raise exceptions on double-close.
        """
        ...
