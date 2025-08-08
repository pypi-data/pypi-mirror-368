"""Configuration validator for Flow SDK.

Validates configuration against the API with fast timeouts and graceful degradation.
"""

import asyncio
from typing import Any, Optional

import httpx

from flow.api.models import Project, ValidationResult


class ConfigValidator:
    """Validates Flow configuration against the API.

    Features:
    - Parallel validation of all fields
    - 500ms hard timeout
    - Graceful degradation on API errors
    """

    def __init__(self, http_client: Optional[httpx.AsyncClient] = None):
        """Initialize validator.

        Args:
            http_client: HTTP client for API calls (creates one if not provided)
        """
        self._client = http_client
        self._owns_client = http_client is None

    async def validate(self, config: dict[str, Any]) -> ValidationResult:
        """Validate configuration against API.

        Args:
            config: Configuration dictionary with api_key, api_url, etc.

        Returns:
            ValidationResult with validation status and available projects
        """
        if not config.get("api_key"):
            return ValidationResult(
                is_valid=False, projects=[], error_message="API key is required"
            )

        # Create client if needed
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(0.5))

        try:
            # Validate API key and fetch projects in parallel
            is_valid, projects = await self._validate_parallel(
                config["api_key"], config.get("api_url", "https://api.mithril.ai")
            )

            if not is_valid:
                return ValidationResult(
                    is_valid=False, projects=[], error_message="Invalid API key"
                )

            return ValidationResult(is_valid=True, projects=projects)

        except asyncio.TimeoutError:
            # API is slow - continue without validation
            return ValidationResult(
                is_valid=True,  # Assume valid to not block user
                projects=[],
                error_message="API is slow, continuing without validation",
            )
        except Exception:
            # Network error - continue without validation
            return ValidationResult(
                is_valid=True,  # Assume valid to not block user
                projects=[],
                error_message="Cannot reach API, continuing without validation",
            )
        finally:
            # Clean up client if we created it
            if self._owns_client and self._client:
                await self._client.aclose()
                self._client = None

    async def _validate_parallel(self, api_key: str, api_url: str) -> tuple[bool, list[Project]]:
        """Validate API key and fetch projects in parallel.

        Args:
            api_key: API key to validate
            api_url: API base URL

        Returns:
            Tuple of (is_valid, projects)
        """
        headers = {"Authorization": f"Bearer {api_key}"}

        # Run both requests in parallel
        tasks = [self._verify_api_key(api_url, headers), self._fetch_projects(api_url, headers)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle results
        # If either task raised an exception, re-raise it to be caught by outer handler
        for result in results:
            if isinstance(result, Exception):
                raise result

        is_valid = results[0] is True
        projects = results[1] if isinstance(results[1], list) else []

        return is_valid, projects

    async def _verify_api_key(self, api_url: str, headers: dict[str, str]) -> bool:
        """Verify API key is valid.

        Args:
            api_url: API base URL
            headers: Request headers with auth

        Returns:
            True if valid, False otherwise

        Raises:
            Exception: Re-raises network errors to be handled at higher level
        """
        response = await self._client.get(f"{api_url}/v2/me", headers=headers)
        return response.status_code == 200

    async def _fetch_projects(self, api_url: str, headers: dict[str, str]) -> list[Project]:
        """Fetch available projects.

        Args:
            api_url: API base URL
            headers: Request headers with auth

        Returns:
            List of available projects
        """
        try:
            response = await self._client.get(f"{api_url}/v2/projects", headers=headers)
            if response.status_code == 200:
                data = response.json()
                return [
                    Project(name=p["name"], region=p.get("region", "us-central1-a")) for p in data
                ]
        except Exception:
            pass

        return []
