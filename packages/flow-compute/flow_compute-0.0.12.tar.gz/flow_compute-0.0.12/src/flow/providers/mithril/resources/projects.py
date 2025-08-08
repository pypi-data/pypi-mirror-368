"""Project resolution component for Mithril provider.

This module provides clean separation of concerns for project name resolution,
following SOLID principles and proper error handling.
"""

import logging
from typing import Dict, List, Optional

from flow._internal.io.http_interfaces import IHttpClient
from flow.errors import FlowError
from flow.utils.instance_parser import is_uuid

from ..api.types import ProjectModel as Project

logger = logging.getLogger(__name__)


class ProjectNotFoundError(FlowError):
    """Raised when a project cannot be resolved."""

    def __init__(self, project_name: str, available_projects: List[str]):
        self.project_name = project_name
        self.available_projects = available_projects

        msg = f"Project '{project_name}' not found."
        if available_projects:
            msg += "\n\nAvailable projects:\n"
            for project in available_projects[:5]:
                msg += f"  • {project}\n"
            if len(available_projects) > 5:
                msg += f"  ... and {len(available_projects) - 5} more"

        super().__init__(msg)


class ProjectResolver:
    """Resolves project names to IDs with caching and error handling."""

    def __init__(self, http_client: IHttpClient):
        """Initialize project resolver.

        Args:
            http_client: HTTP client for API requests
        """
        self.http = http_client
        self._cache: Dict[str, str] = {}  # name -> ID mapping
        self._projects_cache: Optional[List[Project]] = None

    def resolve(self, project_identifier: str) -> str:
        """Resolve project name or ID to project ID.

        Args:
            project_identifier: Project name or UUID

        Returns:
            Project ID (UUID)

        Raises:
            ProjectNotFoundError: If project cannot be resolved
        """
        if not project_identifier:
            raise FlowError("Project identifier is required")

        # If already a UUID, return as is
        if is_uuid(project_identifier):
            logger.debug(f"Project identifier is already a UUID: {project_identifier}")
            return project_identifier

        # Check cache first
        if project_identifier in self._cache:
            logger.debug(f"Resolved project '{project_identifier}' from cache")
            return self._cache[project_identifier]

        # Fetch and resolve
        project_id = self._resolve_from_api(project_identifier)
        if project_id:
            self._cache[project_identifier] = project_id
            logger.info(f"Resolved project '{project_identifier}' to ID: {project_id}")
            return project_id

        # Not found - provide helpful error
        available_names = [p.name for p in self._get_all_projects()]
        raise ProjectNotFoundError(project_identifier, available_names)

    def list_projects(self) -> List[Project]:
        """List all available projects.

        Returns:
            List of Project objects
        """
        return self._get_all_projects()

    def invalidate_cache(self):
        """Clear the cache, forcing fresh lookups."""
        self._cache.clear()
        self._projects_cache = None
        logger.debug("Project resolver cache invalidated")

    def _resolve_from_api(self, project_name: str) -> Optional[str]:
        """Resolve project name using API.

        Args:
            project_name: Project name to resolve

        Returns:
            Project ID if found, None otherwise
        """
        projects = self._get_all_projects()

        # Exact match first
        for project in projects:
            if project.name == project_name:
                return project.fid

        # Case-insensitive match
        name_lower = project_name.lower()
        for project in projects:
            if project.name.lower() == name_lower:
                logger.warning(
                    f"Found case-insensitive match: '{project.name}' for query '{project_name}'"
                )
                return project.fid

        return None

    def _get_all_projects(self) -> List[Project]:
        """Get all projects from API with caching.

        Returns:
            List of Project objects
        """
        if self._projects_cache is not None:
            return self._projects_cache

        try:
            response = self.http.request(
                method="GET",
                url="/v2/projects",
            )

            # API returns list directly
            projects_data = response if isinstance(response, list) else []

            self._projects_cache = [
                Project(
                    fid=p["fid"],
                    name=p["name"],
                    created_at=p["created_at"],
                )
                for p in projects_data
                if "fid" in p and "name" in p and "created_at" in p
            ]

            logger.debug(f"Loaded {len(self._projects_cache)} projects from API")
            return self._projects_cache

        except Exception as e:
            logger.error(f"Failed to fetch projects: {e}")
            # Return empty list instead of failing completely
            return []
