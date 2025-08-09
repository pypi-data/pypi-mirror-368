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

        # Reasonable connection pool/HTTP2 settings for faster handshakes and reuse
        limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)

        # Enable HTTP/2 only if supported or explicitly requested. This avoids requiring 'h2'.
        http2_enabled = False
        try:
            # Respect explicit opt-in via env var
            import os as _os
            if _os.environ.get("FLOW_HTTP2", "").strip() in {"1", "true", "TRUE", "yes", "on"}:
                http2_enabled = True
            else:
                # Best-effort detect if h2 is installed
                import h2  # type: ignore
                _ = h2  # silence linter
                http2_enabled = True
        except Exception:
            http2_enabled = False

        self.client = httpx.Client(
            base_url=base_url,
            headers=headers or {},
            timeout=httpx.Timeout(30.0),
            transport=transport,
            follow_redirects=True,  # Follow redirects automatically
            http2=http2_enabled,
            limits=limits,
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
                        # Demote noisy retry logs to debug; surfaced in higher-level UX instead
                        logger.debug(
                            f"Server error {e.response.status_code} (attempt {attempt + 1}/{max_retries}), "
                            f"retrying in {delay}s"
                        )
                        time.sleep(delay)
                        continue
                    # Build a cleaner server error with helpful suggestions
                    detail_text = None
                    try:
                        data = e.response.json()
                        detail_text = data.get("detail") if isinstance(data, dict) else None
                    except Exception:
                        detail_text = None
                    message_text = (
                        f"Server error {e.response.status_code}: {detail_text}"
                        if detail_text
                        else f"Server error {e.response.status_code}"
                    )
                    last_error = APIError(message_text, status_code=e.response.status_code, response_body=e.response.text)
                    # Attach actionable suggestions for transient 5xx failures
                    try:
                        last_error.suggestions = [
                            "This may be a transient provider issue. Try again in a minute",
                            "If it persists, try a different instance type or region",
                            "Check provider status dashboard",
                            "Run 'flow status' to verify if the request partially succeeded",
                        ]
                    except Exception:
                        pass
                else:
                    # Other client errors - don't retry
                    error_text = e.response.text
                    suggestions: list[str] = []

                    # Try to parse JSON error for structured details
                    detail_text = None
                    try:
                        data = e.response.json()
                        if isinstance(data, dict):
                            detail_text = data.get("detail")
                    except Exception:
                        detail_text = None

                    # Normalize a lowercase aggregate for heuristics
                    combined_lower = " ".join(
                        s for s in [str(detail_text or ""), str(error_text or "")] if s
                    ).lower()

                    # Add helpful message for quota errors
                    if "quota" in combined_lower:
                        # Choose a more specific quotas page when possible
                        try:
                            request_path = url.lower() if isinstance(url, str) else ""
                            # Heuristics to classify storage vs instance quota issues
                            is_storage_context = (
                                "/volumes" in request_path
                                or "volume" in request_path
                                or "storage" in request_path
                                or "volume" in combined_lower
                                or "storage" in combined_lower
                                or "disk" in combined_lower
                            )

                            if is_storage_context:
                                quota_url = "https://app.mithril.ai/storage/quotas"
                            else:
                                quota_url = "https://app.mithril.ai/instances/quotas"

                            error_text += f"\nCheck quota: {quota_url}"
                        except Exception:
                            # Fallback to instances quotas if detection fails
                            error_text += "\nCheck quota: https://app.mithril.ai/instances/quotas"

                    # Price/limit-price too low – provide actionable remediation
                    limit_price_too_low = (
                        e.response.status_code == 400
                        and (
                            "limit price below minimum" in combined_lower
                            or "price below minimum" in combined_lower
                            or "bid price below minimum" in combined_lower
                        )
                    )
                    if limit_price_too_low:
                        # Best-effort: extract the requested limit price from the request body
                        requested_limit = None
                        try:
                            if isinstance(json, dict):
                                lp = json.get("limit_price")
                                if isinstance(lp, str) and lp.strip().startswith("$"):
                                    requested_limit = float(lp.strip().replace("$", ""))
                                elif isinstance(lp, (int, float)):
                                    requested_limit = float(lp)
                        except Exception:
                            requested_limit = None

                        # Suggest a higher cap (simple 25% bump if we know the current)
                        if requested_limit:
                            recommended = round(requested_limit * 1.25, 2)
                            suggestions.extend(
                                [
                                    f"Your current price cap is ${requested_limit:.2f}/hour, which is below the minimum.",
                                    f"Increase the cap and retry: flow run ... --max-price-per-hour {recommended:.2f}",
                                ]
                            )
                        else:
                            suggestions.append(
                                "Increase your price cap and retry (e.g., flow run ... --max-price-per-hour 100)"
                            )

                        # Additional general guidance
                        suggestions.extend(
                            [
                                "Use a higher priority tier to auto-set a higher limit price: flow run ... -p high",
                                "Re-run with --pricing to see the computed limit price in the config table",
                                "If you used 'flow example', export and edit the YAML: flow example <name> --show > job.yaml (add max_price_per_hour) then run: flow run job.yaml",
                            ]
                        )

                    # Add helpful message for name conflicts
                    elif (
                        e.response.status_code == 400 and "name already used" in combined_lower
                    ):
                        error_text += "\n\nHint: Add 'unique_name: true' to your config to automatically generate unique names."

                    api_error = APIError(
                        f"API error {e.response.status_code}: {error_text}",
                        status_code=e.response.status_code,
                        response_body=error_text,
                    )
                    # Attach suggestions when available so CLI can render remediation steps
                    try:
                        if suggestions:
                            api_error.suggestions = suggestions
                    except Exception:
                        pass
                    raise api_error from e

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
