"""I/O operations for Flow SDK.

This package isolates network I/O operations into a dedicated layer to make the
code easier to test, mock, and reason about.

Modules:
- http.py: HTTP client with connection pooling

Note: Storage abstractions live in ``flow.storage`` because storage is largely
provider-specific with shared interfaces at the SDK boundary.
"""

from flow._internal.io.http import HttpClient, HttpClientPool

__all__ = [
    # HTTP
    "HttpClient",
    "HttpClientPool",
]
