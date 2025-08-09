"""I/O operations for Flow SDK.

This package isolates network I/O operations into a dedicated layer.
This separation of concerns makes the code easier to test, mock, and
reason about.

Following John Carmack's principle of directness, each module does
one thing well:
- http.py: HTTP client with connection pooling

Note: Storage abstractions are in the flow.storage package, following
the principle that storage is a provider-specific concern with shared
abstractions.
"""

from .http import HttpClient, HttpClientPool

__all__ = [
    # HTTP
    "HttpClient",
    "HttpClientPool",
]
