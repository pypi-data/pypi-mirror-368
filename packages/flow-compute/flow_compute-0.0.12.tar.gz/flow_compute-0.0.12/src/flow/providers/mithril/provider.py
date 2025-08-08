"""Mithril Provider implementation."""

import logging
import os
import time
import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from rich.console import Console
    from .code_transfer import CodeTransferManager

from httpx import HTTPStatusError as HTTPError

from flow._internal.config import Config, MithrilConfig
from flow._internal.io.http import HttpClientPool
from flow._internal.io.http_interfaces import IHttpClient
from flow.api.models import (
    AvailableInstance,
    Instance,
    InstanceStatus,
    Task,
    TaskConfig,
    TaskStatus,
    User,
    Volume,
)
from flow.core.provider_interfaces import IProvider, IRemoteOperations
from flow.errors import (
    FlowError,
    InsufficientBidPriceError,
    NetworkError,
    ResourceNotAvailableError,
    ResourceNotFoundError,
    TaskNotFoundError,
    TimeoutError,
    ValidationAPIError,
    ValidationError,
)
from flow.errors_pkg.messages import (
    TASK_INSTANCE_NOT_ACCESSIBLE,
    TASK_NOT_FOUND,
    TASK_PENDING_LOGS,
    format_error,
)
from flow.providers.interfaces import IProviderInit
from flow.utils.circuit_breaker import CircuitBreaker
from flow.utils.retry_helper import with_retry

from ..base import ProviderCapabilities
from .adapters.models import MithrilAdapter
from .adapters.mounts import MithrilMountAdapter
from .api.handlers import handle_mithril_errors, validate_response
from .bidding.builder import BidBuilder
from .bidding.finder import AuctionCriteria, AuctionFinder
from .bidding.manager import BidManager
from .core.constants import (
    DEFAULT_REGION,
    DEFAULT_SSH_PORT,
    DEFAULT_SSH_USER,
    DISK_INTERFACE_BLOCK,
    DISK_INTERFACE_FILE,
    MAX_INSTANCES_PER_TASK,
    MAX_VOLUME_SIZE_GB,
    STATUS_MAPPINGS,
    SUPPORTED_REGIONS,
    USER_CACHE_TTL,
    VOLUME_DELETE_TIMEOUT,
    VOLUME_ID_PREFIX,
)
from .core.errors import (
    MithrilAPIError,
    MithrilBidError,
    MithrilError,
    MithrilInstanceError,
)
from .core.models import Auction, MithrilBid, MithrilInstance, MithrilVolume
from .remote_operations import RemoteExecutionError
from .resources.projects import ProjectResolver
from .resources.ssh import SSHKeyManager
from .runtime import MithrilStartupScriptBuilder
from .runtime.script_size import ScriptSizeHandler, ScriptTooLargeError
from .storage import StorageConfig, create_storage_backend
from .volume_operations import VolumeOperations

logger = logging.getLogger(__name__)


class MithrilProvider(IProvider):
    """Mithril implementation of compute and storage providers."""

    # Mithril-specific instance type mappings
    INSTANCE_TYPE_MAPPINGS = {
        # A100 mappings
        "a100": "it_MsIRhxj3ccyVWGfP",
        "1xa100": "it_MsIRhxj3ccyVWGfP",
        "2xa100": "it_5M6aGxGovNeX5ltT",
        "4xa100": "it_fK7Cx6TVhOK5ZfXT",
        "8xa100": "it_J7OyNf9idfImLIFo",
        "a100-80gb.sxm.1x": "it_MsIRhxj3ccyVWGfP",
        "a100-80gb.sxm.2x": "it_5M6aGxGovNeX5ltT",
        "a100-80gb.sxm.4x": "it_fK7Cx6TVhOK5ZfXT",
        "a100-80gb.sxm.8x": "it_J7OyNf9idfImLIFo",
        # H100 mappings - Mithril only offers 8x configurations
        "h100": "it_5ECSoHQjLBzrp5YM",  # Default to 8x SXM
        "1xh100": "it_5ECSoHQjLBzrp5YM",  # Map to 8x (minimum H100 node size)
        "2xh100": "it_5ECSoHQjLBzrp5YM",  # Map to 8x (minimum H100 node size)
        "4xh100": "it_5ECSoHQjLBzrp5YM",  # Map to 8x (minimum H100 node size)
        "8xh100": "it_5ECSoHQjLBzrp5YM",  # 8x SXM variant
        "h100-80gb.sxm.8x": "it_5ECSoHQjLBzrp5YM",
        "h100-80gb.pcie.8x": "it_XqgKWbhZ5gznAYsG",  # Another 8x variant
        # A10 mappings
        "a10": "it_zMPE5XskFP9x2hTb",
        "1xa10": "it_zMPE5XskFP9x2hTb",
        # V100 mappings
        "v100": "it_8l9p3CnK5ZQM7xJd",
        "1xv100": "it_8l9p3CnK5ZQM7xJd",
    }

    def __init__(
        self,
        config: Config,
        http_client: IHttpClient,
        startup_script_builder: MithrilStartupScriptBuilder | None = None,
    ):
        """Initialize Mithril provider.

        Args:
            config: SDK configuration
            http_client: HTTP client for API requests
            startup_script_builder: Builder for startup scripts
        """
        if config.provider != "mithril":
            raise ValueError(f"MithrilProvider requires 'mithril' provider, got: {config.provider}")

        self.config = config
        self.mithril_config = MithrilConfig.from_dict(config.provider_config)
        self.auth_token = config.auth_token

        self.http = http_client
        self.startup_builder = startup_script_builder or MithrilStartupScriptBuilder()
        self.mount_adapter = MithrilMountAdapter()

        # Initialize clean components
        self.project_resolver = ProjectResolver(http_client)
        self.auction_finder = AuctionFinder(http_client)
        self.bid_manager = BidManager(http_client)

        # Initialize script size handler - default to no storage backend for simplicity
        # This ensures scripts work out of the box without configuration

        # Initialize circuit breaker for API calls
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0,
            expected_exceptions=(NetworkError, TimeoutError, HTTPError),
        )
        from .runtime.script_size.handler import ScriptSizeConfig

        # Check if user explicitly wants storage backend (opt-in, not opt-out)
        storage_config = StorageConfig.from_env()
        explicit_storage_request = (
            storage_config is not None or "storage_backend" in config.provider_config
        )

        if explicit_storage_request and storage_config:
            # User explicitly configured storage - validate it's not local
            if "storage_backend" in config.provider_config:
                storage_config.backend_type = config.provider_config["storage_backend"]

            if storage_config.backend_type == "local":
                logger.error(
                    "Local storage backend (127.0.0.1) will NOT work with remote instances. "
                    "Ignoring configuration. Use S3, GCS, or Azure storage instead."
                )
                # Ignore local storage - it's a footgun
                config_without_split = ScriptSizeConfig(enable_split=False)
                self.script_size_handler = ScriptSizeHandler(
                    storage_backend=None, config=config_without_split
                )
            else:
                # Try to use the configured cloud storage
                try:
                    storage_backend = create_storage_backend(storage_config)
                    self.script_size_handler = ScriptSizeHandler(storage_backend=storage_backend)
                    logger.info(
                        f"Using {storage_config.backend_type} storage backend for large scripts. "
                        f"Scripts over 10KB will be uploaded to external storage."
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to initialize {storage_config.backend_type} storage: {e}"
                    )
                    config_without_split = ScriptSizeConfig(enable_split=False)
                    self.script_size_handler = ScriptSizeHandler(
                        storage_backend=None, config=config_without_split
                    )
        else:
            # Default path - no storage backend, use inline + compression only
            logger.info(
                "Using inline script transfer (no external storage). "
                "Scripts up to ~100KB supported with compression."
            )
            config_without_split = ScriptSizeConfig(enable_split=False)
            self.script_size_handler = ScriptSizeHandler(
                storage_backend=None, config=config_without_split
            )

        # Resolve and cache project ID if needed
        self._project_id: str | None = None

        # User cache: stores (user, timestamp) tuples
        self._user_cache: dict[str, tuple[User, float]] = {}
        self._user_cache_ttl = USER_CACHE_TTL

        # Log cache: stores (log_content, timestamp) tuples, keyed by (task_id, tail)
        self._log_cache: dict[tuple[str, int], tuple[str, float]] = {}
        self._log_cache_ttl = 5.0  # 5 seconds cache for logs
        self._log_cache_max_size = 100  # Maximum cache entries
        if self.mithril_config.project:
            try:
                self._project_id = self.project_resolver.resolve(self.mithril_config.project)
                self.ssh_key_manager = SSHKeyManager(http_client, self._project_id)
            except Exception as e:
                logger.warning(f"Failed to resolve project on init: {e}")
                self.ssh_key_manager = SSHKeyManager(http_client)
        else:
            self.ssh_key_manager = SSHKeyManager(http_client)

    @classmethod
    def from_config(cls, config: Config) -> "MithrilProvider":
        """Create Mithril provider from config using connection pooling.

        Args:
            config: SDK configuration

        Returns:
            Initialized Mithril provider
        """
        api_url = config.provider_config.get("api_url", "https://api.mithril.ai")

        # Get pooled HTTP client
        http_client = HttpClientPool.get_client(base_url=api_url, headers=config.get_headers())

        return cls(config=config, http_client=http_client)

    # ============ IComputeProvider Implementation ============

    def normalize_instance_request(
        self, gpu_count: int, gpu_type: str | None = None
    ) -> tuple[str, int, str | None]:
        """Normalize GPU request to valid Mithril instance configuration.

        Mithril-specific constraints:
        - H100s only available in 8-GPU nodes
        - Other GPUs flexible in 1x, 2x, 4x, 8x configurations

        Args:
            gpu_count: Number of GPUs requested by user
            gpu_type: GPU type requested (e.g., "h100", "a100")

        Returns:
            Tuple of (instance_type, num_instances, warning_message)
        """
        if not gpu_type:
            gpu_type = "h100"  # Default to H100

        gpu_type = gpu_type.lower().strip()

        # Handle H100 constraint - they only come in 8x configurations
        if gpu_type == "h100":
            # H100s only available as 8-GPU nodes
            # Round up to nearest multiple of 8
            num_nodes = (gpu_count + 7) // 8  # Ceiling division
            actual_gpus = num_nodes * 8
            warning = None
            if actual_gpus != gpu_count:
                warning = f"H100s only available in 8-GPU nodes. Allocating {actual_gpus} GPUs ({num_nodes} node{'s' if num_nodes > 1 else ''})."
            return "8xh100", num_nodes, warning

        # For other GPU types, use standard configurations
        # Prefer 8x instances for better interconnect
        if gpu_count >= 8 and gpu_count % 8 == 0:
            return f"8x{gpu_type}", gpu_count // 8, None
        elif gpu_count >= 4 and gpu_count % 4 == 0:
            return f"4x{gpu_type}", gpu_count // 4, None
        elif gpu_count >= 2 and gpu_count % 2 == 0:
            return f"2x{gpu_type}", gpu_count // 2, None
        else:
            # Single GPU instances
            return gpu_type, gpu_count, None

    @handle_mithril_errors("Find instances")
    def find_instances(
        self,
        requirements: dict[str, Any],
        limit: int = 10,
    ) -> list[AvailableInstance]:
        """Find available instances matching requirements.

        Args:
            requirements: Dict with keys like instance_type, region, min_gpu_count
            limit: Maximum number of instances to return

        Returns:
            List of available instances
        """
        # Extract requirements
        instance_type = requirements.get("instance_type")
        region = requirements.get("region")
        min_gpu_count = requirements.get("min_gpu_count")
        max_price = requirements.get("max_price_per_hour") or requirements.get("max_price")

        # Resolve instance type if needed
        if instance_type and not instance_type.startswith("it_"):
            instance_type = self._resolve_instance_type(instance_type)

        # Build query parameters
        params = {"limit": str(limit)}
        if instance_type:
            params["instance_type"] = instance_type
        if region:
            params["region"] = region
        if min_gpu_count:
            params["min_gpu_count"] = str(min_gpu_count)
        # Note: max_price filtering done client-side to ensure consistency with mocks

        # Get auctions - API returns list directly
        auctions = self.http.request(
            method="GET",
            url="/v2/spot/availability",
            params=params,
        )

        # Convert auctions to AvailableInstance objects
        available_instances = []
        for auction_data in auctions:
            available_instance = self._convert_auction_to_available_instance(auction_data)
            if available_instance:
                available_instances.append(available_instance)

        # Apply client-side filtering for requirements not handled by API
        filtered_instances = []
        for instance in available_instances:
            # Filter by price if specified
            if max_price is not None and instance.price_per_hour > max_price:
                logger.debug(
                    f"Filtering out {instance.allocation_id} with price {instance.price_per_hour} > {max_price}"
                )
                continue

            # Filter by region if specified (exact match)
            if region and instance.region != region:
                logger.debug(
                    f"Filtering out {instance.allocation_id} with region {instance.region} != {region}"
                )
                continue

            # Skip instance type filtering in client - already handled by server via FID
            # The server filters by FID which is more accurate

            filtered_instances.append(instance)

        return filtered_instances

    def find_optimal_auction(
        self,
        config: TaskConfig,
        use_catalog: bool = True,
    ) -> Auction | None:
        """Find the best auction for the given task configuration.

        This method uses the AuctionFinder to search both API and local catalog
        for auctions that match the requirements, then selects the optimal one
        based on price and availability.

        Args:
            config: Task configuration with requirements
            use_catalog: Whether to include local catalog in search

        Returns:
            Best matching Auction or None if no matches found
        """
        # Build criteria from config
        criteria = AuctionCriteria(
            gpu_type=config.instance_type,
            num_gpus=config.num_instances,
            region=config.region,
            max_price_per_hour=config.max_price_per_hour,
            instance_type=config.instance_type,
        )

        # Fetch all matching auctions
        auctions = self.auction_finder.fetch_auctions(
            from_api=True,
            from_catalog=use_catalog,
            criteria=criteria,
        )

        if not auctions:
            logger.warning("No available instances found matching criteria")
            return None

        # Find matching auctions
        matching = self.auction_finder.find_matching_auctions(auctions, criteria)

        if not matching:
            logger.warning(
                f"No instances match all criteria (found {len(auctions)} total available)"
            )
            return None

        # Sort by price (lowest first) and availability (highest first)
        sorted_auctions = sorted(
            matching,
            key=lambda a: (
                a.price_per_hour or float("inf"),
                -(a.available_gpus or 0),
            ),
        )

        best = sorted_auctions[0]
        logger.info(
            f"Found optimal auction: {best.auction_id} "
            f"({best.gpu_type} @ ${best.price_per_hour}/hr)"
        )

        return best

    def prepare_task_config(self, config: TaskConfig) -> TaskConfig:
        """Prepare task configuration with Mithril-specific defaults.

        Sets default SSH keys and region if not provided by the user.

        Args:
            config: The user-provided task configuration

        Returns:
            Updated task configuration with Mithril defaults applied
        """
        # Make a copy to avoid modifying the original
        prepared = config.model_copy()

        # Set SSH keys from provider config if not specified
        if not prepared.ssh_keys and self.config.provider_config.get("ssh_keys"):
            prepared.ssh_keys = self.config.provider_config["ssh_keys"]

        # DO NOT set region here - let submit_task handle multi-region selection
        # if not prepared.region and self.config.provider_config.get("region"):
        #     prepared.region = self.config.provider_config["region"]

        return prepared

    @handle_mithril_errors("Submit task")
    def submit_task(
        self,
        instance_type: str,
        config: TaskConfig,
        volume_ids: list[str] | None = None,
        allow_partial_fulfillment: bool = False,
        chunk_size: int | None = None,
    ) -> Task:
        """Submit task with automatic instance and region selection.

        Args:
            instance_type: User-friendly instance type (e.g., "a100", "4xa100", "h100")
            config: Task configuration
            volume_ids: Optional list of volume IDs to attach
            allow_partial_fulfillment: Whether to allow partial instance allocation
            chunk_size: Size of chunks for partial fulfillment

        Returns:
            Task object with full details
        """
        # First validate instance type
        try:
            instance_fid = self._resolve_instance_type(instance_type)
        except MithrilInstanceError:
            # Re-raise with the helpful error message
            raise

        # Handle Mithril-specific constraints
        adjusted_config = self._apply_instance_constraints(config, instance_type)

        # Check availability across regions
        availability = self._check_availability(instance_type)

        # Select best region
        selected_region = self._select_best_region(availability, config.region)

        if not selected_region:
            # No availability anywhere
            regions_checked = list(availability.keys()) if availability else ["all regions"]
            raise ResourceNotFoundError(
                f"No {instance_type} instances available",
                suggestions=[
                    f"Checked regions: {', '.join(regions_checked)}",
                    "Try a different instance type",
                    "Increase your max price limit",
                    "Check back later for availability",
                ],
            )

        # Get the auction for the selected region
        auction = availability[selected_region]
        auction_id = auction.fid

        # Update config with selected region if not specified
        if not adjusted_config.region:
            adjusted_config = adjusted_config.model_copy(update={"region": selected_region})

        # Resolve instance type to FID
        instance_type_id = self._resolve_instance_type(instance_type)

        # Get project ID
        project_id = self._get_project_id()

        # Process data_mounts if present
        if adjusted_config.data_mounts:
            # Use generic mount processor to resolve mounts
            from flow._internal.data.mount_processor import MountProcessor

            processor = MountProcessor()
            resolved_mounts = processor.process_mounts(adjusted_config, self)

            # Adapt resolved mounts to Mithril-specific format
            mount_volumes, mount_env = self.mount_adapter.adapt_mounts(resolved_mounts)

            # Add mount volumes to existing volumes list
            volume_ids = list(volume_ids) if volume_ids else []
            volume_ids.extend([v.volume_id for v in mount_volumes if v.volume_id])

            # Update config environment with S3 mount variables
            if mount_env:
                adjusted_config = adjusted_config.model_copy(
                    update={"env": {**adjusted_config.env, **mount_env}}
                )

        # Package local code if requested (only for embedded strategy)
        if adjusted_config.upload_code and not self._should_use_scp_upload(adjusted_config):
            logger.info("Packaging local directory for upload...")
            adjusted_config = self._package_local_code(adjusted_config)

        # Inject minimal Mithril credentials for runtime monitoring
        if adjusted_config.max_run_time_hours:
            runtime_env = {
                "_FLOW_MITHRIL_API_KEY": self.mithril_config.api_key,
                "_FLOW_MITHRIL_API_URL": self.http.base_url,
                "_FLOW_MITHRIL_PROJECT": project_id,
            }
            adjusted_config = adjusted_config.model_copy(
                update={"env": {**adjusted_config.env, **runtime_env}}
            )

        # Build startup script (now includes S3 mounts via environment)
        startup_script_obj = self.startup_builder.build(adjusted_config)
        raw_startup_script = startup_script_obj.content

        # Handle script size limitations
        try:
            prepared_script = self.script_size_handler.prepare_script(raw_startup_script)
            startup_script = prepared_script.content

            if prepared_script.requires_network:
                logger.info(
                    f"Startup script requires network access for download "
                    f"(using {prepared_script.strategy} strategy)"
                )
        except ScriptTooLargeError as e:
            # Provide helpful, user-friendly error message
            size_kb = e.script_size / 1024
            limit_kb = e.max_size / 1024

            # Get tailored suggestions from the handler and augment with SCP guidance
            suggestions = self.script_size_handler._get_failure_suggestions(
                e.script_size, e.strategies_tried
            )
            # De-emphasize external storage backends (not implemented here) and
            # prominently recommend SCP strategy or disabling upload for Colab-like flows
            suggestions.insert(0, "Use upload_strategy='scp' to transfer code after the instance starts (no size limit)")
            suggestions.insert(1, "Or disable code upload: upload_code=False when your image already has what you need")

            # Build error message
            if adjusted_config.upload_code:
                error_msg = (
                    f"Startup script too large ({size_kb:.1f}KB > {limit_kb:.1f}KB limit). "
                    f"This often happens when upload_code=True includes too many files. "
                    f"Try upload_strategy='scp' or upload_code=False."
                )
            else:
                error_msg = (
                    f"Startup script too large ({size_kb:.1f}KB > {limit_kb:.1f}KB limit). "
                    f"The script content exceeds Mithril's size restrictions."
                )

            raise ValidationError(error_msg, suggestions=suggestions[:5]) from e

        # Prepare volume attachments (now includes mount volumes)
        volume_attachments = self._prepare_volume_attachments(volume_ids, adjusted_config)

        # Ensure SSH keys
        ssh_keys = self._get_ssh_keys(adjusted_config)

        # Use the region from config (which was set by _select_best_region)
        # Do NOT override with provider defaults here
        region = adjusted_config.region
        if not region:
            # This should not happen after _select_best_region, but have a fallback
            region = self.mithril_config.region or DEFAULT_REGION

        # Build bid specification using clean builder
        bid_spec = BidBuilder.build_specification(
            config=adjusted_config,
            project_id=project_id,
            region=region,
            auction_id=auction_id,
            instance_type_id=instance_type_id,
            ssh_keys=ssh_keys,
            startup_script=startup_script,
            volume_attachments=volume_attachments,
        )

        # Submit the bid with retry and circuit breaker protection
        def _submit_bid():
            """Inner function for retry logic."""
            return self.http.request(
                method="POST",
                url="/v2/spot/bids",
                json=bid_spec.to_api_payload(),
            )

        # Apply circuit breaker and retry logic
        try:
            # Use retry decorator with task config if available
            retry_config = (
                adjusted_config.retries
                if hasattr(adjusted_config, "retries") and adjusted_config.retries
                else None
            )
            if retry_config:

                @with_retry(
                    max_attempts=retry_config.max_retries,
                    initial_delay=retry_config.initial_delay,
                    max_delay=retry_config.max_delay,
                    exponential_base=retry_config.backoff_coefficient,
                    retriable_exceptions=(NetworkError, TimeoutError, HTTPError),
                )
                def _submit_with_retry():
                    return self._circuit_breaker.call(_submit_bid)

                response = _submit_with_retry()
            else:
                # Default retry behavior
                @with_retry(
                    max_attempts=3,
                    initial_delay=1.0,
                    retriable_exceptions=(NetworkError, TimeoutError, HTTPError),
                )
                def _submit_with_retry():
                    return self._circuit_breaker.call(_submit_bid)

                response = _submit_with_retry()
        except ValidationAPIError as e:
            # Check if this is a price-related validation error
            if self._is_price_validation_error(e):
                # Enhance the error with current pricing information
                enhanced_error = self._enhance_price_error(
                    e, instance_type_id, region, config.max_price_per_hour
                )
                raise enhanced_error from e
            else:
                # Re-raise other validation errors as-is
                raise

        # Extract bid ID from response
        try:
            bid_id = self._extract_bid_id(response)
        except Exception as e:
            raise MithrilBidError(
                f"Failed to create bid for task '{adjusted_config.name}': {e}"
            ) from e

        logger.info(
            f"Created bid {bid_id} for task '{adjusted_config.name}' "
            f"({'spot' if auction_id else 'on-demand'})"
        )

        # Build initial Task object
        initial_bid_data = {
            "fid": bid_id,
            "task_name": adjusted_config.name,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "instance_type": instance_type_id,
            "num_instances": adjusted_config.num_instances,
            "region": region,
            "price_per_hour": (
                f"${adjusted_config.max_price_per_hour:.2f}"
                if adjusted_config.max_price_per_hour
                else "$0"
            ),
            "instances": [],
        }

        task = self._build_task_from_bid(initial_bid_data, adjusted_config)

        # Handle SCP-based code upload if configured
        if adjusted_config.upload_code and self._should_use_scp_upload(adjusted_config):
            logger.info("Task submitted. Code will be uploaded after instance starts.")
            # Store task config for later reference
            task._upload_pending = True
            task._upload_config = adjusted_config

            # Start async upload process
            try:
                self._initiate_scp_upload(task, adjusted_config)
            except Exception as e:
                logger.warning(
                    f"Failed to initiate SCP upload: {e}. Code upload may need to be done manually."
                )

        return task

    @handle_mithril_errors("Get task")
    def get_task(self, task_id: str) -> Task:
        """Get full Task object with all details.

        Args:
            task_id: ID of the task (internally a 'bid' in Mithril API)

        Returns:
            Task object with current information
        """
        # Try cache first for basic info (for quick display)
        from flow.cli.utils.task_index_cache import TaskIndexCache

        cache = TaskIndexCache()
        cached_task = cache.get_cached_task(task_id)

        # Always fetch fresh data for accurate status, but use cache for instant display
        # Mithril doesn't support individual bid GET, so we list and filter
        project_id = self._get_project_id()
        response = self.http.request(
            method="GET", url="/v2/spot/bids", params={"project": project_id}
        )

        # Response might be a list directly or have 'data' key with list of bids
        if isinstance(response, list):
            bids = response
        else:
            bids = response.get("data", [])

        # Find our bid
        bid = next((b for b in bids if b.get("fid") == task_id), None)
        if not bid:
            # If not found but we have cache, the task might have been terminated
            if cached_task:
                raise TaskNotFoundError(
                    f"Task {task_id} no longer exists (was: {cached_task.get('status')})"
                )
            raise TaskNotFoundError(format_error(TASK_NOT_FOUND, task_id=task_id))

        # Build and return Task object with instance details
        return self._build_task_from_bid(bid, fetch_instance_details=True)

    def get_task_ssh_connection_info(self, task_id: str) -> tuple[Path | None, str]:
        """Get SSH connection info for a task.

        Public method to get SSH key path for connecting to a task.

        Args:
            task_id: ID of the task

        Returns:
            Tuple of (ssh_key_path, error_message)
            If successful, returns (Path, "")
            If failed, returns (None, error_message)
        """
        # Try cache first for instant response
        from flow.cli.utils.ssh_key_cache import SSHKeyCache

        ssh_cache = SSHKeyCache()
        cached_path = ssh_cache.get_key_path(task_id)
        if cached_path:
            return Path(cached_path), ""

        # Not cached, do full lookup
        bid = self._get_bid(task_id)
        ssh_key_path, error_msg = self._prepare_ssh_access(bid)

        # Cache successful resolution
        if ssh_key_path:
            ssh_cache.save_key_path(task_id, str(ssh_key_path))

        return ssh_key_path, error_msg

    @handle_mithril_errors("Get task status")
    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get current status of a task.

        Args:
            task_id: ID of the task (internally a 'bid' in Mithril API)

        Returns:
            Current task status
        """
        # Mithril doesn't support individual bid GET, so we list and filter
        project_id = self._get_project_id()

        # Apply retry logic for status checks
        @with_retry(
            max_attempts=3,
            initial_delay=0.5,
            retriable_exceptions=(NetworkError, TimeoutError, HTTPError),
        )
        def _get_status():
            return self._circuit_breaker.call(
                lambda: self.http.request(
                    method="GET", url="/v2/spot/bids", params={"project": project_id}
                )
            )

        response = _get_status()

        # Response might be a list directly or have 'data' key with list of bids
        if isinstance(response, list):
            bids = response
        else:
            bids = response.get("data", [])

        # Find our bid
        bid = next((b for b in bids if b.get("fid") == task_id), None)
        if not bid:
            raise TaskNotFoundError(format_error(TASK_NOT_FOUND, task_id=task_id))

        # Get status from bid
        mithril_status = bid.get("status", "Pending")
        return self._map_mithril_status_to_enum(mithril_status)

    def stop_task(self, task_id: str) -> bool:
        """Stop a running task.

        Args:
            task_id: ID of the task to stop

        Returns:
            True if successful
        """
        try:
            # Use v2 endpoint for cancellation (DELETE method)
            self.http.request(
                method="DELETE",
                url=f"/v2/spot/bids/{task_id}",
            )
            return True
        except Exception as e:
            logger.error(f"Failed to stop task {task_id}: {e}")
            return False

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task.

        Deprecated: Use stop_task instead.

        Args:
            task_id: ID of the task to cancel

        Returns:
            True if successful
        """
        return self.stop_task(task_id)

    def terminate_task(self, task_id: str) -> bool:
        """Terminate a running task.

        Alias for stop_task to match expected interface.

        Args:
            task_id: ID of the task to terminate

        Returns:
            True if successful
        """
        return self.stop_task(task_id)

    def get_logs(self, task_id: str, tail: int = 100) -> str:
        """Get logs for a task.

        Alias for get_task_logs to match expected interface.

        Args:
            task_id: ID of the task
            tail: Number of lines to return

        Returns:
            Log content as string
        """
        return self.get_task_logs(task_id, tail=tail)

    @handle_mithril_errors("Get user")
    def get_user(self, user_id: str) -> User:
        """Fetch user information from Mithril profile API.

        Args:
            user_id: User ID like 'user_kfV4CCaapLiqCNlv'

        Returns:
            User object with username and email

        Raises:
            ResourceNotFoundError: If user not found
            APIError: If API request fails
        """
        # Check cache
        if cached := self._user_cache.get(user_id):
            user, timestamp = cached
            if time.time() - timestamp < self._user_cache_ttl:
                return user
            del self._user_cache[user_id]

        # Make API call to profile endpoint
        try:
            response = self.http.request(method="GET", url=f"/v2/users/{user_id}")

            # Extract user data
            user_data = response.get("data", {})
            user = User(
                user_id=user_id,
                username=user_data.get("username", "unknown"),
                email=user_data.get("email", "unknown@example.com"),
            )

            # Cache the result
            self._user_cache[user_id] = (user, time.time())
            return user

        except HTTPError as e:
            if e.response.status_code == 404:
                raise ResourceNotFoundError(f"User {user_id} not found")
            raise

    def get_task_instances(self, task_id: str) -> list[Instance]:
        """Get all instances for a task with full details including IPs.

        Args:
            task_id: Task ID (bid FID)

        Returns:
            List of Instance objects with IP addresses populated

        Raises:
            TaskNotFoundError: If task doesn't exist
            APIError: If API request fails
        """
        # First get the bid to have context
        bid = self._get_bid(task_id)

        instances = []
        instance_ids = bid.get("instances", [])

        for instance_id in instance_ids:
            if isinstance(instance_id, str):
                # Need to fetch full instance details
                try:
                    instance_data = self._get_instance(instance_id)
                    instance = MithrilAdapter.mithril_instance_to_instance(
                        MithrilInstance(**instance_data), MithrilBid(**bid)
                    )
                    instances.append(instance)
                except Exception as e:
                    logger.warning(f"Failed to fetch instance {instance_id}: {e}")
                    # Create partial instance with just ID
                    instances.append(
                        Instance(
                            instance_id=instance_id,
                            task_id=task_id,
                            status=InstanceStatus.PENDING,
                            created_at=datetime.now(),
                        )
                    )
            elif isinstance(instance_id, dict):
                # Already have instance data
                try:
                    instance = MithrilAdapter.mithril_instance_to_instance(
                        MithrilInstance(**instance_id), MithrilBid(**bid)
                    )
                    instances.append(instance)
                except Exception as e:
                    logger.warning(f"Failed to parse instance data: {e}")

        return instances

    def _get_instance(self, instance_id: str) -> dict:
        """Get detailed instance information from API."""
        response = self.http.request(
            method="GET", url="/v2/spot/instances", params={"id": instance_id}
        )

        instances = response.get("data", [])
        if not instances:
            raise ResourceNotFoundError(f"Instance {instance_id} not found")

        return instances[0]

    def _get_bid(self, task_id: str) -> dict:
        """Get bid information for a task."""
        project_id = self._get_project_id()
        response = self.http.request(
            method="GET", url="/v2/spot/bids", params={"id": task_id, "project": project_id}
        )

        bids = response.get("data", [])
        if not bids:
            raise TaskNotFoundError(format_error(TASK_NOT_FOUND, task_id=task_id))

        return bids[0]

    def _prepare_ssh_access(self, bid: dict) -> tuple[Path | None, str]:
        """Prepare SSH access for a task by finding matching local keys.

        Args:
            bid: Bid data containing SSH key information

        Returns:
            Tuple of (matching_private_key_path, error_message)
            If successful, returns (Path, "")
            If failed, returns (None, error_message)
        """
        # Check if task was created with SSH access
        # SSH keys are in the launch_specification
        launch_spec = bid.get("launch_specification", {})
        bid_ssh_keys = launch_spec.get("ssh_keys", [])

        # Even if no SSH keys in bid, we'll try to find available keys
        # This matches the behavior of the SSH command which clearly works

        # Try to find matching local SSH key using smart resolution
        import os

        from flow.core.ssh_resolver import SmartSSHKeyResolver

        ssh_resolver = SmartSSHKeyResolver(self.ssh_key_manager)

        # First check if MITHRIL_SSH_KEY environment variable is set
        if os.environ.get("MITHRIL_SSH_KEY"):
            ssh_key_path = Path(os.environ["MITHRIL_SSH_KEY"])
            if ssh_key_path.exists():
                return ssh_key_path, ""

        # If we have SSH keys in the bid, try to match them
        if bid_ssh_keys:
            for ssh_key_id in bid_ssh_keys:
                # First try platform SSH key resolution (existing behavior)
                private_key_path = self.ssh_key_manager.find_matching_local_key(ssh_key_id)
                if private_key_path:
                    return private_key_path, ""

                # Then try smart resolution for config-specified keys
                resolved_path = ssh_resolver.resolve_ssh_key(ssh_key_id)
                if resolved_path:
                    return resolved_path, ""

        # Try common SSH key locations as a last resort
        common_key_paths = [
            Path.home() / ".ssh" / "test_flow_key",
            Path.home() / ".ssh" / "flow_key",
            Path.home() / ".ssh" / "id_rsa",
            Path.home() / ".ssh" / "id_ed25519",
            Path.home() / ".ssh" / "id_ecdsa",
        ]

        for key_path in common_key_paths:
            if key_path.exists():
                # Found a key, let's try it
                return key_path, ""

        # No matching key found - build helpful error message
        key_names = []
        for key_id in bid_ssh_keys[:3]:  # Show first 3 keys
            key = self.ssh_key_manager.get_key(key_id)
            if key:
                key_names.append(f"'{key.name}' ({key_id})")
            else:
                key_names.append(key_id)

        keys_desc = ", ".join(key_names)
        if len(bid_ssh_keys) > 3:
            keys_desc += f" and {len(bid_ssh_keys) - 3} more"

        # List available local keys
        available_keys = []
        for path in common_key_paths:
            if path.exists():
                available_keys.append(str(path))

        error_msg = f"Task requires SSH key {keys_desc} but couldn't match with local keys.\n"
        if available_keys:
            error_msg += "\nFound local SSH keys:\n"
            for key in available_keys:
                error_msg += f"  - {key}\n"
        error_msg += "\nTo fix this:\n"
        error_msg += "  1. Use 'flow ssh-keys list' to see all platform keys\n"
        error_msg += "  2. Set MITHRIL_SSH_KEY=/path/to/private/key\n"
        error_msg += "  3. Or run 'flow init' to reconfigure SSH keys"

        return None, error_msg

    def _build_ssh_command(
        self,
        ssh_host: str,
        command: str,
        private_key_path: Path | None = None,
        timeout: int = 30,
        log_level: str = "ERROR",
    ) -> list[str]:
        """Build SSH command with proper options and optional private key.

        Args:
            ssh_host: SSH host to connect to
            command: Command to execute on remote host
            private_key_path: Optional path to private key
            timeout: Connection timeout in seconds
            log_level: SSH log level

        Returns:
            List of command arguments for subprocess
        """
        ssh_cmd = [
            "ssh",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            f"ConnectTimeout={timeout}",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            f"LogLevel={log_level}",
        ]

        # Add identity file if provided
        if private_key_path:
            ssh_cmd.extend(["-i", str(private_key_path)])
            logger.debug(f"Using SSH key: {private_key_path}")

        # Add host and command
        ssh_cmd.extend([f"{DEFAULT_SSH_USER}@{ssh_host}", command])

        return ssh_cmd

    @handle_mithril_errors("get task logs")
    def get_task_logs(
        self,
        task_id: str,
        tail: int = 100,
        log_type: str = "stdout",
    ) -> str:
        """Retrieve last N lines of task logs via SSH.

        Uses the remote operations interface for consistent SSH handling,
        ensuring the same SSH mechanism is used as for 'flow ssh'.

        Args:
            task_id: ID of the task
            tail: Number of lines to return
            log_type: Type of logs (stdout, stderr, or both)

        Returns:
            Log content as string
        """
        # Get task details to check status
        bid = self._get_bid(task_id)
        bid_status = bid.get("status", "").lower()

        # Check if task was cancelled
        if bid_status == "cancelled":
            return (
                f"Task {task_id} was cancelled. Logs are not available because "
                "instances are terminated upon cancellation. Consider using "
                "'flow status' to check task outcomes."
            )

        # Check if task is still pending (Mithril uses "Open" for pending)
        instances = bid.get("instances", [])
        if not instances or bid_status in ["pending", "open"]:
            # Get elapsed time for better user feedback
            created_at_str = bid.get("created_at")
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    elapsed = (datetime.now(timezone.utc) - created_at).total_seconds()
                    task_ref = task_id if not task_id.startswith("bid_") else "the task"
                    return format_error(TASK_PENDING_LOGS, task_id=task_ref)
                except (ValueError, TypeError) as e:
                    logger.debug(
                        f"Failed to parse created_at timestamp: {created_at_str}, error: {e}"
                    )
            task_ref = task_id if not task_id.startswith("bid_") else "the task"
            return format_error(TASK_PENDING_LOGS, task_id=task_ref)

        # Build command to get Docker logs
        # Determine a docker container name if any (fallback to startup logs)
        # Use a POSIX-safe command that picks the first container name when present.
        if log_type == "both":
            command = (
                "CN=$(docker ps -a --format '{{.Names}}' | head -n1); "
                "if [ -n \"$CN\" ]; then "
                f"  echo '=== Docker container logs ===' && docker logs \"$CN\" --tail {tail} 2>&1; "
                "else "
                "  echo 'Task logs not available yet. Showing startup logs...' && "
                "  LOG=/var/log/foundry/startup_script.log; "
                "  if [ -s \"$LOG\" ]; then "
                f"    sudo tail -n {tail} \"$LOG\"; "
                "  else "
                "    echo 'Startup logs are empty (instance may still be starting).'; "
                f"    echo '  • Wait and re-run: flow logs {task_id}'; "
                f"    echo '  • Test connectivity: flow ssh {task_id}'; "
                "  fi; "
                "fi"
            )
        elif log_type == "stderr":
            command = (
                "CN=$(docker ps -a --format '{{.Names}}' | head -n1); "
                "if [ -n \"$CN\" ]; then "
                f"  docker logs \"$CN\" --tail {tail} 2>&1 >/dev/null; "
                "else "
                "  echo 'No stderr logs available (no container running).'; "
                f"  echo 'Try stdout or startup logs: flow logs {task_id}'; "
                "fi"
            )
        else:
            command = (
                "CN=$(docker ps -a --format '{{.Names}}' | head -n1); "
                "if [ -n \"$CN\" ]; then "
                f"  docker logs \"$CN\" --tail {tail}; "
                "else "
                "  echo 'Task logs not available yet. Showing startup logs...' && "
                "  LOG=/var/log/foundry/startup_script.log; "
                "  if [ -s \"$LOG\" ]; then "
                f"    sudo tail -n {tail} \"$LOG\"; "
                "  else "
                "    echo 'Startup logs are empty (instance may still be starting).'; "
                f"    echo '  • Wait and re-run: flow logs {task_id}'; "
                f"    echo '  • Test connectivity: flow ssh {task_id}'; "
                "  fi; "
                "fi"
            )

        # Check cache first
        cache_key = (task_id, tail, log_type)
        if cached := self._log_cache.get(cache_key):
            log_content, timestamp = cached
            if time.time() - timestamp < self._log_cache_ttl:
                # Cache hit - return cached content
                return log_content
            # Cache expired - remove it
            del self._log_cache[cache_key]

        # Clean cache if it's too large
        if len(self._log_cache) > self._log_cache_max_size:
            # Remove oldest entries
            current_time = time.time()
            expired_keys = [
                key
                for key, (_, ts) in self._log_cache.items()
                if current_time - ts > self._log_cache_ttl
            ]
            for key in expired_keys:
                del self._log_cache[key]

            # If still too large, remove oldest half
            if len(self._log_cache) > self._log_cache_max_size:
                sorted_items = sorted(
                    self._log_cache.items(),
                    key=lambda x: x[1][1],  # Sort by timestamp
                )
                for key, _ in sorted_items[: len(sorted_items) // 2]:
                    del self._log_cache[key]

        # Use remote operations to execute the command - this is the DRY approach
        # that ensures we use the same SSH mechanism as 'flow ssh'
        try:
            remote_ops = self.get_remote_operations()
            log_content = remote_ops.execute_command(task_id, command)

            # Cache successful results
            self._log_cache[cache_key] = (log_content.strip(), time.time())

            return log_content.strip() if log_content else "No logs available"

        except RemoteExecutionError as e:
            error_msg = str(e).lower()

            # Provide specific error messages based on failure type
            if "no ssh access" in error_msg:
                return format_error(TASK_INSTANCE_NOT_ACCESSIBLE, task_id=task_id)
            elif "ssh key resolution failed" in error_msg:
                return (
                    "SSH key resolution failed. To fix:\n"
                    "  1. Run 'flow init' to configure SSH keys\n"
                    "  2. Or set MITHRIL_SSH_KEY=/path/to/private/key\n"
                    "  3. Or place SSH key in ~/.ssh/ with standard naming"
                )
            elif "connection refused" in error_msg or "connection timed out" in error_msg:
                from .core.constants import EXPECTED_PROVISION_MINUTES

                return (
                    "Instance not reachable. This could mean:\n"
                    f"  1. Instance is still starting (Mithril instances take up to {EXPECTED_PROVISION_MINUTES} minutes)\n"
                    "  2. Security group blocking SSH (port 22)\n"
                    "  3. Network connectivity issues\n"
                    "Try 'flow ssh' to test connectivity"
                )
            elif "instance may still be starting" in error_msg or "not ready" in error_msg:
                # This is from our new intelligent retry
                return (
                    "SSH is not ready yet. The instance is still starting up.\n"
                    "\n"
                    "Try 'flow ssh' which will automatically wait for the instance to be ready."
                )
            elif "permission denied" in error_msg:
                return (
                    "SSH authentication failed. To fix:\n"
                    "  1. Ensure your SSH key matches the one used to create the task\n"
                    "  2. Check SSH keys with 'flow whoami'\n"
                    "  3. Reconfigure with 'flow init' if needed"
                )
            else:
                # Generic error - but still provide helpful context
                logger.debug(f"Failed to get logs for task {task_id}: {e}")
                return (
                    f"Failed to retrieve logs: {str(e)}\n"
                    "Try 'flow ssh' to test connectivity and manually check logs"
                )

        except Exception as e:
            logger.error(f"Unexpected error getting logs for task {task_id}: {e}")
            return f"Failed to retrieve logs: {str(e)}"

    @handle_mithril_errors("stream task logs")
    def stream_task_logs(
        self,
        task_id: str,
        log_type: str = "stdout",
    ) -> Iterator[str]:
        """Stream task logs in real-time.

        Note: Real-time streaming requires paramiko or asyncssh.
        This implementation polls for new content periodically.

        Args:
            task_id: ID of the task
            log_type: Type of logs (stdout or stderr)

        Yields:
            Log lines as they become available
        """
        import subprocess
        import time

        task = self.get_task(task_id)

        if not task:
            yield f"Error: Task {task_id} not found"
            return

        bid_status = task.status.value.lower()

        instances = [task.ssh_host] if task.ssh_host else []

        # Check if task was cancelled
        if bid_status == "cancelled":
            yield (
                f"Task {task_id} was cancelled. Logs are not available because "
                "instances are terminated upon cancellation."
            )
            return

        if not instances:
            from .core.constants import EXPECTED_PROVISION_MINUTES

            yield "Task pending - waiting for instance to start..."
            yield f"Note: Mithril instances typically take up to {EXPECTED_PROVISION_MINUTES} minutes to become available."
            yield ""
            # Poll until instance is available
            while not task.ssh_host:
                time.sleep(5)
                # Refresh task data
                task = self.get_task(task_id)
                if task.ssh_host:
                    break
                if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    yield f"Task is no longer running (status: {task.status.value})"
                    return

        if not task.ssh_host:
            yield "Instance not accessible - no SSH destination available"
            yield "The instance may still be starting. Try 'flow status' to check."
            return

        ssh_host = task.ssh_host

        private_key_path, error_msg = self.get_task_ssh_connection_info(task_id)

        # If SSH key preparation failed but we still have instance SSH info,
        # try to find a key anyway (SSH might still work)
        if error_msg and ssh_host:
            # Try to find any available SSH key as a fallback
            from flow.core.ssh_resolver import SmartSSHKeyResolver

            ssh_resolver = SmartSSHKeyResolver(self.ssh_key_manager)

            # Try common SSH key locations
            for key_name in ["id_rsa", "id_ed25519", "id_ecdsa"]:
                key_path = Path.home() / ".ssh" / key_name
                if key_path.exists():
                    private_key_path = key_path
                    logger.debug(f"Using fallback SSH key: {key_path}")
                    break

            # If still no key, check if MITHRIL_SSH_KEY env var is set
            if not private_key_path and os.environ.get("MITHRIL_SSH_KEY"):
                env_key_path = Path(os.environ["MITHRIL_SSH_KEY"])
                if env_key_path.exists():
                    private_key_path = env_key_path
                    logger.debug(f"Using SSH key from MITHRIL_SSH_KEY env var: {env_key_path}")

            # If we found a key, clear the error message
            if private_key_path:
                error_msg = ""

        # If we still don't have an SSH key, yield the original error
        if error_msg:
            yield error_msg
            return

        # Check if Docker container exists
        check_command = "CN=$(docker ps -a --format '{{.Names}}' | head -n1); [ -n \"$CN\" ] && echo 'exists' || echo 'not_found'"
        check_cmd = self._build_ssh_command(ssh_host, check_command, private_key_path)
        check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=30)

        using_docker = check_result.returncode == 0 and check_result.stdout.strip() == "exists"

        if not using_docker:
            # Fallback to startup log if Docker container doesn't exist
            log_file = "/var/log/foundry/startup_script.log"
            yield "Task logs not available yet. Showing startup logs..."
            yield ""
        else:
            # We'll use docker logs with --follow
            log_file = None  # Not used for Docker
        last_size = 0
        consecutive_failures = 0
        max_consecutive_failures = 3

        while True:
            try:
                # Get current file size
                stat_command = f"sudo stat -c %s {log_file} 2>/dev/null || echo 0"
                size_cmd = self._build_ssh_command(
                    ssh_host, stat_command, private_key_path, timeout=5
                )

                size_result = subprocess.run(size_cmd, capture_output=True, text=True, timeout=30)

                if size_result.returncode != 0:
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        yield f"\n[Connection lost after {consecutive_failures} retries. Attempting to reconnect...]"
                        # Exponential backoff for reconnection
                        time.sleep(min(consecutive_failures * 2, 30))
                    else:
                        yield f"[Connection issue, retry {consecutive_failures}/{max_consecutive_failures}]"
                        time.sleep(2)
                    continue

                # Reset failure counter on success
                consecutive_failures = 0

                try:
                    current_size = int(size_result.stdout.strip())
                except ValueError:
                    current_size = 0

                # If file has grown, get new content
                if current_size > last_size:
                    # Get new content from last position
                    tail_command = f"sudo tail -c +{last_size + 1} {log_file} 2>/dev/null"
                    content_cmd = self._build_ssh_command(
                        ssh_host, tail_command, private_key_path, timeout=5
                    )

                    content_result = subprocess.run(
                        content_cmd, capture_output=True, text=True, timeout=30
                    )
                    if content_result.returncode == 0 and content_result.stdout:
                        # Yield each new line
                        for line in content_result.stdout.splitlines():
                            yield line
                    elif content_result.returncode != 0:
                        # Log read failed, but don't break - might be temporary
                        logger.warning(f"Failed to read new log content: {content_result.stderr}")

                    last_size = current_size

                # Check if task is complete
                try:
                    task = self.get_task(task_id)
                    if task.status in [
                        TaskStatus.COMPLETED,
                        TaskStatus.FAILED,
                        TaskStatus.CANCELLED,
                    ]:
                        yield f"\n[Task {task.status.value}. Fetching final logs...]"
                        # Get any final logs with retry
                        try:
                            final_logs = self.get_task_logs(task_id, tail=50)
                            final_lines = final_logs.splitlines()
                            if final_lines:
                                yield "\n[Final log entries:]"
                                for line in final_lines[-10:]:
                                    yield line
                        except Exception as e:
                            yield f"[Failed to retrieve final logs: {e}]"
                        break
                except Exception as e:
                    # Don't break on task status check failure
                    logger.warning(f"Failed to check task status: {e}")

                # Wait before next poll
                time.sleep(2)

            except subprocess.TimeoutExpired:
                consecutive_failures += 1
                yield f"[SSH timeout, retry {consecutive_failures}/{max_consecutive_failures}]"
                if consecutive_failures >= max_consecutive_failures:
                    yield "[Multiple timeouts. Connection may be lost. Continuing to retry...]"
                    time.sleep(5)
            except KeyboardInterrupt:
                yield "\n[Log streaming interrupted by user]"
                break
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"Error in log streaming: {e}")
                yield f"[Streaming error: {str(e)}. Retry {consecutive_failures}/{max_consecutive_failures}]"
                if consecutive_failures >= max_consecutive_failures:
                    yield "[Maximum retries exceeded. Stopping log stream.]"
                    task_ref = task_id if not task_id.startswith("bid_") else "the task"
                    yield f"[To manually check logs, run: flow logs {task_ref}]"
                    break
                time.sleep(min(consecutive_failures * 2, 10))

    @handle_mithril_errors("List tasks")
    def list_tasks(
        self,
        status: TaskStatus | None = None,
        limit: int = 100,
        force_refresh: bool = False,
    ) -> list[Task]:
        """List tasks, newest first.

        Args:
            status: Filter by status
            limit: Maximum number of tasks to return
            force_refresh: Bypass any caching for real-time data

        Returns:
            List of Task objects, sorted newest first
        """
        import time

        start_total = time.time()

        # Map Flow TaskStatus to Mithril bid status
        # Note: Mithril uses specific capitalization for status values
        status_map = {
            TaskStatus.RUNNING: "Allocated",  # Mithril uses "Allocated" for running instances
            TaskStatus.PENDING: "Open",
            TaskStatus.CANCELLED: "Terminated",
            TaskStatus.COMPLETED: "Terminated",  # Completed tasks are also "Terminated" in Mithril
            TaskStatus.FAILED: "Terminated",  # Failed tasks are also "Terminated" in Mithril
        }

        # Fetch tasks with newest-first ordering from API
        seen_task_ids = set()  # Track seen tasks for deduplication
        unique_tasks = []  # Maintain order while deduplicating
        next_cursor = None
        page_count = 0
        last_cursor = None  # Track to detect stuck pagination

        # Fetch pages until we have enough tasks or hit limit
        max_pages = 10  # Safety limit to prevent infinite loops

        api_time = 0
        build_time = 0

        # Fetch extra to ensure we have enough after deduplication
        while page_count < max_pages and len(unique_tasks) < limit * 2:
            page_count += 1
            params = {
                "project": self._get_project_id(),
                "limit": str(100),  # Always fetch max per page
                "sort_by": "created_at",  # Use correct parameter name
                "sort_dir": "desc",  # Request newest first from API
            }

            if status:
                mithril_status = status_map.get(status)
                if mithril_status:
                    params["status"] = mithril_status
                    logger.debug(
                        f"Filtering for Mithril status: {mithril_status} (from TaskStatus.{status.name})"
                    )

            if next_cursor:
                params["cursor"] = next_cursor

            # Add cache-busting parameter when force refresh is requested
            if force_refresh:
                import random
                import time

                params["_cache_bust"] = f"{int(time.time())}-{random.randint(1000, 9999)}"

            logger.debug(f"Fetching page {page_count} with params: {params}")
            start_api = time.time()
            response = self.http.request(
                method="GET",
                url="/v2/spot/bids",
                params=params,
            )
            api_time += time.time() - start_api
            logger.debug(
                f"Page {page_count} returned {len(response.get('data', []))} bids in {api_time:.3f}s"
            )

            bids = response.get("data", [])
            if not bids:
                break

            start_build = time.time()
            for bid in bids:
                task_id = bid.get("fid", "")
                if task_id and task_id not in seen_task_ids:
                    seen_task_ids.add(task_id)
                    # For running tasks, check if we should fetch instance details
                    fetch_details = False
                    if bid.get("status", "").lower() in ["allocated", "running"]:
                        # Check if task has been running for more than 5 minutes
                        created_at_str = bid.get("created_at")
                        if created_at_str:
                            try:
                                created_at = datetime.fromisoformat(
                                    created_at_str.replace("Z", "+00:00")
                                )
                                elapsed = (datetime.now(timezone.utc) - created_at).total_seconds()
                                # Fetch details for tasks running more than 5 minutes
                                fetch_details = elapsed > 300
                            except (ValueError, TypeError):
                                pass

                    task = self._build_task_from_bid(bid, fetch_instance_details=fetch_details)
                    unique_tasks.append(task)
            build_time += time.time() - start_build

            next_cursor = response.get("next_cursor")

            # Detect stuck pagination (same cursor returned)
            if next_cursor and next_cursor == last_cursor:
                logger.debug(f"Pagination returned same cursor at page {page_count}")
                break

            last_cursor = next_cursor

            if not next_cursor:
                break

        # API should return newest first with proper sort_by/sort_dir params
        # Local sorting ensures correct order if API doesn't sort as expected
        start_sort = time.time()
        unique_tasks.sort(key=lambda t: t.created_at, reverse=True)
        sort_time = time.time() - start_sort

        # Log timing details
        total_time = time.time() - start_total
        logger.info(
            f"list_tasks timing: total={total_time:.3f}s, api={api_time:.3f}s ({page_count} pages), build={build_time:.3f}s, sort={sort_time:.3f}s, tasks={len(unique_tasks)}"
        )

        # Return requested limit
        return unique_tasks[:limit]

    def list_active_tasks(self, limit: int = 100) -> list[Task]:
        """List currently active (allocated/running) tasks.

        This is a convenience method that filters for allocated bids,
        which represent actively running tasks in Mithril.

        Args:
            limit: Maximum number of tasks to return

        Returns:
            List of active Task objects
        """
        return self.list_tasks(status=TaskStatus.RUNNING, limit=limit)

    # ============ IStorageProvider Implementation ============

    def _get_project_id(self) -> str:
        """Get resolved project ID with proper error handling.

        Returns:
            Project ID

        Raises:
            MithrilError: If project cannot be resolved
        """
        if self._project_id:
            return self._project_id

        if not self.mithril_config.project:
            raise MithrilError("Project is required but not configured")

        # Try to resolve
        try:
            self._project_id = self.project_resolver.resolve(self.mithril_config.project)
            return self._project_id
        except Exception as e:
            raise MithrilError(
                f"Failed to resolve project '{self.mithril_config.project}': {e}"
            ) from e

    def _resolve_instance_type(self, instance_spec: str) -> str:
        """Resolve instance type specification to ID.

        Args:
            instance_spec: Instance type name or UUID

        Returns:
            Instance type ID

        Raises:
            MithrilInstanceError: If instance type cannot be resolved
        """
        if not instance_spec:
            raise MithrilInstanceError("Instance type specification is required")

        if instance_spec.startswith("it_"):
            return instance_spec

        try:
            return self._resolve_instance_type_simple(instance_spec)
        except ValueError as e:
            raise MithrilInstanceError(str(e)) from e

    def _package_local_code(self, config: TaskConfig) -> TaskConfig:
        """Package local code directory for upload.

        Creates a gzipped tar archive of the current working directory,
        excluding common development artifacts and respecting .flowignore
        patterns. The archive is base64-encoded and embedded in the task
        configuration for extraction on the remote instance.

        Args:
            config: Task configuration to update with code archive.

        Returns:
            TaskConfig: Updated configuration with code archive in environment.

        Raises:
            ValidationError: If compressed archive exceeds 10MB limit.
        """
        import base64
        import os
        import tarfile
        import tempfile
        from pathlib import Path

        # Get current working directory
        cwd = Path.cwd()

        # Create excludes list
        excludes = {
            ".git",
            "__pycache__",
            "*.pyc",
            ".env",
            ".venv",
            "venv",
            "node_modules",
            ".DS_Store",
            "*.log",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
            ".coverage",
            "htmlcov",
            ".idea",
            ".vscode",
            "*.egg-info",
            "dist",
            "build",
        }

        # Check for .flowignore file
        flowignore_path = cwd / ".flowignore"
        if flowignore_path.exists():
            with open(flowignore_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        excludes.add(line)

        # Create temporary tar.gz file
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_file:
            try:
                with tarfile.open(tmp_file.name, "w:gz") as tar:
                    # Add all files from current directory with relative paths
                    for root, dirs, files in os.walk(cwd):
                        root_path = Path(root)

                        # Filter directories
                        dirs[:] = [
                            d
                            for d in dirs
                            if not any((root_path / d).match(pattern) for pattern in excludes)
                        ]

                        # Add files
                        for file in files:
                            file_path = root_path / file
                            # Skip excluded files
                            if any(file_path.match(pattern) for pattern in excludes):
                                continue

                            # Add with relative path from cwd
                            rel_path = file_path.relative_to(cwd)
                            tar.add(file_path, arcname=str(rel_path))

                # Check size
                size_bytes = os.path.getsize(tmp_file.name)
                size_mb = size_bytes / (1024 * 1024)

                logger.info(f"Code archive size: {size_mb:.2f}MB")

                if size_mb > 10:  # 10MB limit
                    raise ValidationError(
                        f"Project size ({size_mb:.1f}MB) exceeds limit (10MB)",
                        suggestions=[
                            "Use .flowignore to exclude unnecessary files",
                            "Build a Docker image with your code",
                            "Use flow.run(..., upload_code=False) with a pre-built image",
                        ],
                    )

                # Read and encode
                with open(tmp_file.name, "rb") as f:
                    code_archive = base64.b64encode(f.read()).decode("ascii")

                # Pass code archive to startup script builder via environment.
                # The _FLOW_CODE_ARCHIVE variable is extracted by the builder
                # and passed to CodeUploadSection for script generation.
                updated_env = config.env.copy()
                updated_env["_FLOW_CODE_ARCHIVE"] = code_archive

                return config.model_copy(update={"env": updated_env})

            finally:
                # Clean up temp file
                os.unlink(tmp_file.name)

    def _should_use_scp_upload(self, config: TaskConfig) -> bool:
        """Determine if SCP upload should be used instead of embedded.

        Args:
            config: Task configuration

        Returns:
            True if SCP upload should be used
        """
        # Check explicit strategy
        if config.upload_strategy == "scp":
            return True
        elif config.upload_strategy in ["embedded", "none"]:
            return False

        # Auto mode - decide based on project size
        # Estimate compressed size (rough heuristic)
        cwd = Path.cwd()
        total_size = 0
        file_count = 0

        # Get exclude patterns
        excludes = self._get_exclude_patterns()

        try:
            for root, dirs, files in os.walk(cwd):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(Path(root, d).match(p) for p in excludes)]

                for file in files:
                    file_path = Path(root) / file
                    if any(file_path.match(p) for p in excludes):
                        continue

                    try:
                        total_size += file_path.stat().st_size
                        file_count += 1
                    except OSError:
                        continue

            # Estimate compressed size (typically 30-50% of original)
            estimated_compressed = total_size * 0.4

            # Use SCP if estimated compressed size > 8KB (leaving margin for base64 overhead)
            if estimated_compressed > 8 * 1024:
                logger.info(
                    f"Auto-selected SCP upload: {file_count} files, "
                    f"~{estimated_compressed / 1024:.1f}KB compressed"
                )
                return True
            else:
                logger.info(
                    f"Auto-selected embedded upload: {file_count} files, "
                    f"~{estimated_compressed / 1024:.1f}KB compressed"
                )
                return False

        except Exception as e:
            logger.warning(f"Error estimating project size: {e}. Using embedded upload.")
            return False

    def _initiate_scp_upload(self, task: Task, config: TaskConfig) -> None:
        """Initiate SCP-based code upload in background.

        Args:
            task: Task to upload code to
            config: Task configuration
        """
        # For now, we'll implement synchronous upload
        # In future, this could be made async with threading/asyncio
        import threading

        def upload_worker():
            try:
                logger.info(f"Starting background code upload for task {task.task_id}")

                # Create transfer manager
                transfer_manager = self._create_transfer_manager()

                # Configure upload
                from .code_transfer import CodeTransferConfig

                transfer_config = CodeTransferConfig(
                    source_dir=Path.cwd(),
                    target_dir="/workspace",
                    ssh_timeout=config.upload_timeout,
                    transfer_timeout=config.upload_timeout,
                )

                # The transfer_code_to_task method will properly wait for SSH
                # using the ssh_waiter which implements exponential backoff
                result = transfer_manager.transfer_code_to_task(task, transfer_config)

                logger.info(
                    f"Code upload completed for {task.task_id}: "
                    f"{result.files_transferred} files, {result.transfer_rate}"
                )

            except Exception as e:
                logger.error(f"Background code upload failed for {task.task_id}: {e}")
                import traceback

                logger.debug(f"Traceback: {traceback.format_exc()}")

        # Start upload in background thread
        thread = threading.Thread(target=upload_worker, daemon=True)
        thread.start()

    def _create_transfer_manager(self) -> "CodeTransferManager":
        """Create a code transfer manager instance.

        Returns:
            Configured CodeTransferManager
        """
        from .code_transfer import CodeTransferManager
        from .ssh_waiter import ExponentialBackoffSSHWaiter
        from .transfer_strategies import RsyncTransferStrategy

        return CodeTransferManager(
            provider=self,
            ssh_waiter=ExponentialBackoffSSHWaiter(self),
            transfer_strategy=RsyncTransferStrategy(),
            progress_reporter=None,  # CLI will provide its own reporter
        )

    def upload_code_to_task(
        self,
        task_id: str,
        source_dir: Path | None = None,
        timeout: int = 600,
        console: Optional["Console"] = None,
        *,
        target_dir: str = "~",
        progress_reporter: Optional["IProgressReporter"] = None,
    ) -> "TransferResult":
        """Upload code to an existing task using SCP.

        Public method for manual code uploads via CLI.

        Args:
            task_id: Task to upload to
            source_dir: Source directory (default: current directory)
            timeout: Upload timeout in seconds
            console: Optional Rich console to use for output (creates new if not provided)
        """
        task = self.get_task(task_id)

        if not task.ssh_host:
            raise FlowError(
                f"Task {task_id} does not have SSH access",
                suggestions=[
                    "Check that the task is running: flow status " + task_id,
                    "SSH access may not be available for this task type",
                ],
            )

        # Create transfer manager with CLI progress reporter
        from rich.console import Console

        from .code_transfer import CodeTransferConfig, CodeTransferManager, RichProgressReporter

        # Use provided console or create new one
        if console is None:
            console = Console()
        reporter_to_use = progress_reporter or RichProgressReporter(console)

        transfer_manager = CodeTransferManager(provider=self, progress_reporter=reporter_to_use)

        # Configure and execute upload
        config = CodeTransferConfig(
            source_dir=source_dir or Path.cwd(),
            target_dir=target_dir,
            ssh_timeout=timeout,
            transfer_timeout=timeout,
        )

        result = transfer_manager.transfer_code_to_task(task, config)

        # Print concise summary for UX
        try:
            if result.bytes_transferred == 0 and result.files_transferred == 0:
                # Provide clear, contextual no-op message
                task_ref = task.name or task.task_id
                src = str(config.source_dir)
                dst = target_dir
                console.print(
                    f"[dim]No changes to sync ({src} → {task_ref}:{dst})[/dim]"
                )
            else:
                size_mb = (result.bytes_transferred or 0) / (1024 * 1024)
                console.print(
                    f"[green]✓[/green] Upload complete: {result.files_transferred} files, {size_mb:.1f} MB → {(task.name or task.task_id)}:{target_dir} @ {result.transfer_rate}"
                )
        except Exception:
            # Avoid failing UX on print issues
            pass

        logger.info(
            f"Code uploaded successfully to {task_id} - "
            f"Files: {result.files_transferred}, "
            f"Size: {result.bytes_transferred / (1024 * 1024):.1f} MB, "
            f"Rate: {result.transfer_rate}"
        )
        return result

    def _get_exclude_patterns(self) -> list[str]:
        """Get file patterns to exclude from code upload."""
        # Default excludes
        patterns = [
            ".git",
            "__pycache__",
            "*.pyc",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "*.egg-info",
            ".venv",
            "venv",
            "node_modules",
            ".DS_Store",
        ]

        # Add .flowignore patterns if present
        flowignore = Path.cwd() / ".flowignore"
        if flowignore.exists():
            with open(flowignore) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)

        return patterns

    def _prepare_volume_attachments(
        self, volume_ids: list[str] | None, config: TaskConfig
    ) -> list[dict[str, Any]]:
        """Prepare volume attachment specifications.

        Args:
            volume_ids: Optional list of volume IDs or names
            config: Task configuration for mount paths

        Returns:
            List of volume attachment dicts
        """
        if not volume_ids:
            return []

        # Resolve volume names to IDs
        resolved_ids = []
        volumes = self.list_volumes()  # Get all volumes for name resolution

        for identifier in volume_ids:
            # Check if it's already a volume ID
            if self.is_volume_id(identifier):
                resolved_ids.append(identifier)
            else:
                # Try to find by name
                matches = [v for v in volumes if v.name == identifier]
                if len(matches) == 1:
                    resolved_ids.append(matches[0].id)
                elif len(matches) > 1:
                    raise ValidationError(
                        f"Multiple volumes found with name '{identifier}'. "
                        f"Please use the volume ID instead."
                    )
                else:
                    # Try partial match
                    partial_matches = [
                        v for v in volumes if v.name and identifier.lower() in v.name.lower()
                    ]
                    if len(partial_matches) == 1:
                        resolved_ids.append(partial_matches[0].id)
                    else:
                        raise ValidationError(
                            f"No volume found matching '{identifier}'. "
                            f"Use 'flow volumes list' to see available volumes."
                        )

        attachments = []
        for i, volume_id in enumerate(resolved_ids):
            # Get mount path from config or use default
            if i < len(config.volumes) and config.volumes[i].mount_path:
                mount_path = config.volumes[i].mount_path
            else:
                mount_path = f"/data{i}"

            attachments.append(
                BidBuilder.format_volume_attachment(
                    volume_id=volume_id, mount_path=mount_path, mode="rw"
                )
            )

        return attachments

    def _get_ssh_keys(self, config: TaskConfig) -> list[str]:
        """Get SSH keys for the task.

        Args:
            config: Task configuration

        Returns:
            List of SSH key IDs
        """
        # Resolution priority: task config > provider config > auto-generation.
        requested_keys = config.ssh_keys or self.mithril_config.ssh_keys

        if requested_keys:
            # Use explicitly requested keys
            platform_keys = self.ssh_key_manager.ensure_platform_keys(requested_keys)
            if not platform_keys:
                logger.warning("No SSH keys could be resolved from requested keys")
            return platform_keys

        # No keys specified. Check for existing Mithril-specific keys or auto-generate.
        logger.debug("No SSH keys specified, checking for existing Mithril keys")

        # Check for existing platform keys for this project.
        existing_keys = self.ssh_key_manager.list_keys()
        if existing_keys:
            logger.info(f"Using {len(existing_keys)} existing Mithril SSH keys")
            return [key.fid for key in existing_keys]

        # No existing keys found. Auto-generate a new Mithril-specific key.
        logger.info("No SSH keys found, auto-generating Mithril-specific SSH key")

        # Attempt to auto-generate a key.
        generated_key_id = self.ssh_key_manager.auto_generate_key()
        if generated_key_id:
            logger.info(f"Successfully generated Mithril SSH key: {generated_key_id}")
            return [generated_key_id]

        # Return empty list if auto-generation fails.
        logger.warning(
            "Failed to auto-generate SSH key. Tasks will fail without SSH access. "
            "Please manually add an SSH key using: flow ssh-keys add"
        )
        return []

    def _extract_bid_id(self, response: Any) -> str:
        """Extract bid ID from API response.

        Args:
            response: API response

        Returns:
            Bid ID

        Raises:
            MithrilBidError: If bid ID cannot be extracted
        """
        if isinstance(response, dict):
            bid_id = response.get("fid") or response.get("bid_id")
            if bid_id:
                return bid_id
            raise MithrilBidError(f"No bid ID in response: {response}")

        # Fallback for non-dict responses
        bid_id = str(response)
        if not bid_id:
            raise MithrilBidError(f"Invalid bid response: {response}")

        return bid_id

    def _generate_short_id(self) -> str:
        """Generate a short unique ID for volume names.

        Uses base36 encoding (0-9, a-z) for compact representation.
        Returns 6 characters which gives us ~2 billion unique values.
        """
        import string

        # Use timestamp + random for uniqueness
        # Take last 8 digits of timestamp to keep it short
        timestamp_part = int(time.time() * 1000) % 100000000
        random_part = uuid.uuid4().int % 1000

        # Combine and convert to base36
        combined = timestamp_part + random_part

        # Base36 encoding
        chars = string.digits + string.ascii_lowercase
        result = []
        while combined and len(result) < 6:
            combined, remainder = divmod(combined, 36)
            result.append(chars[remainder])

        # Pad with random chars if needed
        while len(result) < 6:
            result.append(chars[uuid.uuid4().int % 36])

        return "".join(reversed(result))

    @handle_mithril_errors("Create volume")
    def create_volume(
        self,
        size_gb: int,
        name: str | None = None,
        interface: str = "block",
    ) -> Volume:
        """Create a new storage volume.

        Args:
            size_gb: Size of the volume in GB
            name: Optional name for the volume
            interface: Storage type - "block" (default) or "file"

        Returns:
            Created Volume object
        """
        # Get resolved project ID
        project_id = self._get_project_id()

        # Get current region
        region = self.mithril_config.region or DEFAULT_REGION

        # Regional validation - hardcoded but helpful
        if region == "us-central1-b":
            if interface == "file":
                raise ValidationError(
                    f"File storage not available in {region}. "
                    f"Use us-central1-a instead for file storage."
                )
            if size_gb > 7168:  # 7TB
                raise ValidationError(
                    f"Maximum volume size in {region} is 7TB (requested {size_gb}GB). "
                    f"For larger volumes, use us-central1-a or eu-central1-a."
                )

        # General size validation
        if size_gb > MAX_VOLUME_SIZE_GB:
            raise ValidationError(f"Volume size {size_gb}GB exceeds maximum {MAX_VOLUME_SIZE_GB}GB")

        # Map interface parameter to Mithril constants
        disk_interface = DISK_INTERFACE_FILE if interface == "file" else DISK_INTERFACE_BLOCK

        volume_payload = {
            "size_gb": size_gb,
            # Generate a short unique ID using base36 (0-9, a-z)
            # This gives us ~2 billion unique values in 6 chars
            "name": name or f"flow-vol-{self._generate_short_id()}",
            "project": project_id,  # API expects 'project', not 'project_id'
            "disk_interface": disk_interface,
            "region": region,
        }

        try:
            response = self.http.request(
                method="POST",
                url="/v2/volumes",
                json=volume_payload,
            )

            # Validate response
            response = validate_response(response, ["fid"])
        except MithrilAPIError as e:
            # Handle specific error cases for file shares
            if e.status_code == 400 and interface == "file":
                # Check if error is about file share availability
                error_msg = str(e).lower()
                if "file" in error_msg or "disk_interface" in error_msg:
                    raise ResourceNotAvailableError(
                        f"File shares not available in region {self.mithril_config.region}",
                        suggestions=[
                            "Use block storage: interface='block'",
                            "Check https://docs.mithril.ai/regions for file share availability",
                            "Contact support to request file share access in this region",
                        ],
                    ) from e
            raise

        # Create Mithril volume model from API response
        mithril_volume = MithrilVolume(
            fid=response["fid"],
            name=response.get("name", volume_payload["name"]),
            size_gb=size_gb,
            region=response.get("region", self.mithril_config.region or DEFAULT_REGION),
            status=response.get("status", "available"),  # Add required status field
            created_at=response.get("created_at", datetime.now().isoformat()),
            attached_to=response.get("attached_to", []),
            mount_path=response.get("mount_path"),
        )

        # Use adapter to convert to domain model
        return MithrilAdapter.mithril_volume_to_volume(mithril_volume)

    @handle_mithril_errors("Delete volume")
    def delete_volume(self, volume_id: str) -> bool:
        """Delete a volume.

        Volume deletion is synchronous and may take 30-60 seconds while
        the API unmounts and deallocates storage.

        Args:
            volume_id: ID of the volume to delete

        Returns:
            True if successful

        Raises:
            MithrilVolumeError: If deletion fails
        """
        # Use context manager for timeout adjustment
        from contextlib import contextmanager

        import httpx

        @contextmanager
        def extended_timeout(client, timeout_seconds: float):
            """Temporarily extend HTTP client timeout."""
            original = client.timeout
            client.timeout = httpx.Timeout(timeout_seconds)
            try:
                yield
            finally:
                client.timeout = original

        with extended_timeout(self.http.client, float(VOLUME_DELETE_TIMEOUT)):
            self.http.request(
                method="DELETE",
                url=f"/v2/volumes/{volume_id}",
            )

        return True

    def list_volumes(self, limit: int = 100) -> list[Volume]:
        """List all volumes.

        Args:
            limit: Maximum number of volumes to return

        Returns:
            List of Volume objects
        """
        project_id = self._get_project_id()
        region = self.mithril_config.region or DEFAULT_REGION
        response = self.http.request(
            method="GET",
            url="/v2/volumes",
            params={
                "project": project_id,
                "region": region,
                "limit": str(limit),
                "sort_by": "created_at",
                "sort_dir": "desc",
            },
        )
        # Handle both list and wrapped response formats
        volumes_data = (
            response
            if isinstance(response, list)
            else response.get("data", response.get("volumes", []))
        )

        volumes = []
        for vol_data in volumes_data:
            # Create Mithril volume model from API response
            # API returns 'capacity_gb' not 'size_gb'
            size_gb = vol_data.get("capacity_gb", 0)

            mithril_volume = MithrilVolume(
                fid=vol_data.get("fid"),
                name=vol_data.get("name"),
                size_gb=size_gb,
                region=vol_data.get("region", DEFAULT_REGION),
                status=vol_data.get("status", "available"),  # Add required status field
                created_at=vol_data.get("created_at", datetime.now().isoformat()),
                attached_to=vol_data.get("attached_to", []),
                mount_path=vol_data.get("mount_path"),
            )

            # Use adapter to convert to domain model
            volume = MithrilAdapter.mithril_volume_to_volume(mithril_volume)
            volumes.append(volume)

        return volumes

    def upload_file(
        self,
        volume_id: str,
        local_path: Path,
        remote_path: str | None = None,
    ) -> bool:
        """Upload file to volume.

        Args:
            volume_id: ID of the volume
            local_path: Local file path
            remote_path: Remote path in volume

        Returns:
            True if successful
        """
        try:
            # Read file content
            with open(local_path, "rb") as f:
                content = f.read()

            # Upload via API
            upload_payload = {
                "volume_id": volume_id,
                "path": remote_path or local_path.name,
                "content": content.decode("utf-8") if content else "",
            }

            self.http.request(
                method="POST",
                url=f"/volumes/{volume_id}/upload",
                json=upload_payload,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to upload file to volume {volume_id}: {e}")
            return False

    def upload_directory(
        self,
        volume_id: str,
        local_path: Path,
        remote_path: str | None = None,
    ) -> bool:
        """Upload directory to volume.

        Args:
            volume_id: ID of the volume
            local_path: Local directory path
            remote_path: Remote path in volume

        Returns:
            True if successful
        """
        try:
            # For now, upload files one by one
            # Bulk upload optimization is available through the S3 client's
            # multipart upload feature for files larger than 5MB
            success = True
            for file_path in local_path.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(local_path)
                    remote_file_path = (
                        f"{remote_path}/{relative_path}" if remote_path else str(relative_path)
                    )
                    if not self.upload_file(volume_id, file_path, remote_file_path):
                        success = False
            return success
        except Exception as e:
            logger.error(f"Failed to upload directory to volume {volume_id}: {e}")
            return False

    def download_file(
        self,
        volume_id: str,
        remote_path: str,
        local_path: Path,
    ) -> bool:
        """Download file from volume.

        Args:
            volume_id: ID of the volume
            remote_path: Remote file path in volume
            local_path: Local destination path

        Returns:
            True if successful
        """
        try:
            response = self.http.request(
                method="GET",
                url=f"/volumes/{volume_id}/download",
                params={"path": remote_path},
            )

            # Write content to file
            content = response.get("content", "")
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, "w") as f:
                f.write(content)

            return True
        except Exception as e:
            logger.error(f"Failed to download file from volume {volume_id}: {e}")
            return False

    def download_directory(
        self,
        volume_id: str,
        remote_path: str,
        local_path: Path,
    ) -> bool:
        """Download directory from volume.

        Args:
            volume_id: ID of the volume
            remote_path: Remote directory path in volume
            local_path: Local destination path

        Returns:
            True if successful
        """
        try:
            # List files in directory
            response = self.http.request(
                method="GET",
                url=f"/volumes/{volume_id}/list",
                params={"path": remote_path},
            )

            files = response.get("files", [])
            success = True

            for file_info in files:
                remote_file_path = file_info.get("path")
                if remote_file_path:
                    # Calculate local path
                    relative_path = remote_file_path.replace(remote_path, "").lstrip("/")
                    local_file_path = local_path / relative_path

                    if not self.download_file(volume_id, remote_file_path, local_file_path):
                        success = False

            return success
        except Exception as e:
            logger.error(f"Failed to download directory from volume {volume_id}: {e}")
            return False

    def is_volume_id(self, identifier: str) -> bool:
        """Check if identifier is a volume ID (vs a volume name).

        Mithril volume IDs start with 'vol_' prefix.

        Args:
            identifier: String that might be a volume ID or name

        Returns:
            True if this is a volume ID, False if it's a name
        """
        return identifier.startswith(VOLUME_ID_PREFIX)

    def mount_volume(self, volume_id: str, task_id: str, mount_point: str | None = None) -> None:
        """Mount a volume to a running task.

        Args:
            volume_id: Volume ID or name to mount
            task_id: Task ID to mount the volume to
            mount_point: Optional custom mount path (default: /mnt/{volume_name})

        Raises:
            ResourceNotFoundError: If task or volume not found
            ValidationError: If region mismatch or already attached
            MithrilAPIError: If API update fails
            RemoteExecutionError: If SSH mount fails
        """
        # Get task and volume
        task = self.get_task(task_id)
        if not task:
            raise TaskNotFoundError(format_error(TASK_NOT_FOUND, task_id=task_id))

        # Resolve volume ID if name provided
        resolved_volume_id = volume_id
        if not self.is_volume_id(volume_id):
            volumes = self.list_volumes()
            matches = [v for v in volumes if v.name == volume_id]
            if len(matches) == 1:
                resolved_volume_id = matches[0].id
            elif len(matches) > 1:
                raise ValidationError(
                    f"Multiple volumes found with name '{volume_id}'. "
                    f"Please use the volume ID instead."
                )
            else:
                # Try partial match
                partial_matches = [
                    v for v in volumes if v.name and volume_id.lower() in v.name.lower()
                ]
                if len(partial_matches) == 1:
                    resolved_volume_id = partial_matches[0].id
                else:
                    raise ResourceNotFoundError(f"Volume '{volume_id}' not found")

        # Get volume details
        volumes = self.list_volumes()
        volume = next((v for v in volumes if v.id == resolved_volume_id), None)
        if not volume:
            raise ResourceNotFoundError(f"Volume '{resolved_volume_id}' not found")

        # Validate region match
        if task.region != volume.region:
            raise ValidationError(
                f"Cannot mount volume '{volume.name or volume.id}' ({volume.id}) to task '{task.name or task.task_id}' ({task.task_id}):\n"
                f"  - Volume region: {volume.region}\n"
                f"  - Task region: {task.region}\n"
                f"Volumes must be in the same region as tasks.\n\n"
                f"Solutions:\n"
                f"  1. Create a new volume in {task.region}:\n"
                f"     flow create-volume --size {volume.size_gb} --name {volume.name}-{task.region} --region {task.region}\n"
                f"  2. Use a different volume in {task.region}:\n"
                f"     flow volumes list | grep {task.region}"
            )

        # Check if already attached to this task
        task_instances = set(task.instances)
        if volume.attached_to and any(inst in task_instances for inst in volume.attached_to):
            raise ValidationError(
                f"Volume '{volume.name or volume.id}' already attached to this task"
            )

        # Critical: Block volumes cannot be mounted to multiple instances
        if len(task.instances) > 1:
            # Check if this is a file share (which supports multi-attach)
            if hasattr(volume, "interface") and volume.interface == "file":
                logger.info(
                    f"File share volume {volume.id} can be mounted to all {len(task.instances)} instances"
                )
            else:
                raise ValidationError(
                    f"Cannot mount block volume to multi-instance task:\n"
                    f"  - Task '{task.name or task.task_id}' has {len(task.instances)} instances\n"
                    f"  - Block volumes can only be attached to one instance at a time\n\n"
                    f"Solutions:\n"
                    f"  1. Use a file share volume instead (supports multi-instance access)\n"
                    f"  2. Mount to a single-instance task\n"
                    f"  3. Use Mithril's upcoming instance-specific mount feature (not yet available)"
                )

        # Get current bid to extract volumes
        project_id = self._get_project_id()
        response = self.http.request(
            method="GET", url="/v2/spot/bids", params={"project": project_id}
        )
        bids = response if isinstance(response, list) else response.get("data", [])
        bid = next((b for b in bids if b.get("fid") == task_id), None)
        if not bid:
            raise TaskNotFoundError(format_error(TASK_NOT_FOUND, task_id=task_id))

        # Extract current volumes from launch specification
        launch_spec = bid.get("launch_specification", {})
        current_volumes = launch_spec.get("volumes", [])

        # Determine next mount device
        next_device_letter = chr(100 + len(current_volumes))  # d, e, f, ...
        # Use custom mount point if provided, otherwise default
        if mount_point:
            mount_path = mount_point
        else:
            mount_path = f"/mnt/{volume.name or f'volume-{next_device_letter}'}"

        # Update bid with new volume - requires pausing first
        updated_volumes = current_volumes + [resolved_volume_id]

        # Update volumes with proper state management
        try:
            # Pause bid (idempotent)
            self._pause_bid(task_id)

            # Update volumes while paused
            self._update_bid_volumes(task_id, updated_volumes)

            # Unpause bid (idempotent)
            self._unpause_bid(task_id)

        except Exception as e:
            # Always attempt to unpause on error
            self._safe_unpause_bid(task_id)

            # Provide clear error message
            if "already paused" in str(e).lower():
                raise MithrilAPIError(
                    "Failed to update volumes: Bid state conflict. "
                    "The bid may be in transition. Please try again in a few seconds."
                ) from e
            else:
                raise MithrilAPIError(f"Failed to update bid volumes: {e}") from e

        # Check if instance is ready for SSH operations
        task_status = bid.get("status", "").lower()

        # Volume is now attached to the bid, but mount may need to wait
        if task_status not in ["allocated", "running"] or not self._is_instance_ssh_ready(task):
            # Volume is attached but instance not ready for mount
            logger.info(
                f"Volume {volume.name or volume.id} attached to task {task.name or task.task_id}. "
                f"Mount will complete when instance is ready."
            )

            # Return early - volume is attached, mount will happen via startup script
            # or user can manually mount when SSH is available
            return

        # Instance is ready, attempt immediate mount
        logger.debug("Instance appears ready, attempting immediate mount via SSH")

        try:
            # Use remote operations to execute mount command
            from .remote_operations import MithrilRemoteOperations

            remote_ops = MithrilRemoteOperations(self)

            # Generate mount script using shared volume operations
            # For runtime mounts, we start counting from existing volumes
            volume_index = len(current_volumes)
            is_file_share = hasattr(volume, "interface") and volume.interface == "file"

            mount_script = VolumeOperations.generate_mount_script(
                volume_index=volume_index,
                mount_path=mount_path,
                volume_id=volume.id if is_file_share else None,
                format_if_needed=True,  # Format if unformatted
                add_to_fstab=False,  # Don't persist runtime mounts by default
                is_file_share=is_file_share,
            )

            # Wrap in sudo for remote execution
            mount_cmd = f"sudo bash -c '{mount_script}'"

            remote_ops.execute_command(task_id, mount_cmd, timeout=30)

            # Verify mount succeeded
            verify_cmd = f"mountpoint -q {mount_path} && echo MOUNTED || echo FAILED"
            result = remote_ops.execute_command(task_id, verify_cmd, timeout=10)

            if "FAILED" in result:
                # Mount command succeeded but mount isn't present
                logger.warning(
                    f"Mount command executed but volume not mounted at {mount_path}. "
                    f"Volume is attached and will be available on next reboot."
                )
            else:
                logger.debug(
                    f"Successfully mounted and verified volume {volume.name or volume.id} at {mount_path}"
                )

        except Exception as e:
            # SSH mount failed, but volume is still attached successfully
            # Don't rollback - the attachment succeeded!
            error_msg = str(e).lower()

            if "ssh" in error_msg or "not responding" in error_msg or "connection" in error_msg:
                # SSH not ready - this is expected for new instances
                logger.info(
                    f"Volume attached successfully. SSH mount deferred: {e}. "
                    f"Volume will be available at {mount_path} when instance is ready."
                )
                # Return success - volume IS attached
                return
            else:
                # Unexpected error during mount - log but don't fail
                logger.warning(
                    f"Volume attached but mount failed: {e}. "
                    f"Manual mount may be required at {mount_path}"
                )
                return

    def _pause_bid(self, bid_id: str) -> None:
        """Pause a bid (idempotent operation).

        Args:
            bid_id: Bid ID to pause

        Raises:
            MithrilAPIError: If pause request fails
        """
        try:
            self.http.request(
                method="PATCH",
                url=f"/v2/spot/bids/{bid_id}",
                json={"paused": True},
            )
            logger.debug(f"Bid {bid_id} pause request succeeded")
        except Exception as e:
            # Check if already paused (idempotent operation)
            if "already paused" in str(e).lower():
                logger.debug(f"Bid {bid_id} already paused")
                return
            raise MithrilAPIError(f"Failed to pause bid: {e}") from e

        # Small delay to let state propagate before volume update
        # No verification - trust the successful API response
        time.sleep(1.0)

    def _unpause_bid(self, bid_id: str) -> None:
        """Unpause a bid (idempotent operation).

        Args:
            bid_id: Bid ID to unpause
        """
        try:
            self.http.request(
                method="PATCH",
                url=f"/v2/spot/bids/{bid_id}",
                json={"paused": False},
            )
        except Exception as e:
            # Check if already unpaused (idempotent operation)
            if "not paused" in str(e).lower() or "already running" in str(e).lower():
                logger.debug(f"Bid {bid_id} already unpaused")
                return
            raise

    def _safe_unpause_bid(self, bid_id: str) -> None:
        """Attempt to unpause a bid, ignoring errors.

        Args:
            bid_id: Bid ID to unpause
        """
        try:
            self._unpause_bid(bid_id)
        except Exception:
            logger.warning(f"Failed to unpause bid {bid_id} during error recovery")

    def _update_bid_volumes(self, bid_id: str, volumes: list[str]) -> None:
        """Update volumes for a paused bid.

        Args:
            bid_id: Bid ID to update
            volumes: List of volume IDs to attach

        Raises:
            MithrilAPIError: If update fails
        """
        self.http.request(
            method="PATCH",
            url=f"/v2/spot/bids/{bid_id}",
            json={"volumes": volumes},
        )

    def get_storage_capabilities(self, location: str | None = None) -> dict[str, Any] | None:
        """Get storage capabilities by region.

        Args:
            location: Optional specific region to query. If None, returns all regions.

        Returns:
            Dictionary of storage capabilities by region, or None if not implemented.
        """
        # Hardcoded capabilities based on Mithril documentation
        all_caps = {
            "us-central1-a": {
                "types": ["block", "file"],
                "max_gb": 15360,  # 15TB
                "available": True,
            },
            "us-central1-b": {"types": ["block"], "max_gb": 7168, "available": True},  # 7TB
            "eu-central1-a": {"types": ["block"], "max_gb": 15360, "available": True},  # 15TB
            "eu-central1-b": {"types": ["block"], "max_gb": 15360, "available": True},  # 15TB
        }

        if location:
            return {
                location: all_caps.get(location, {"types": [], "max_gb": 0, "available": False})
            }
        return all_caps

    def _is_instance_ssh_ready(self, task: Task) -> bool:
        """Check if instance is ready for SSH operations.

        Args:
            task: Task to check

        Returns:
            True if SSH is likely ready, False otherwise
        """
        # Quick check if SSH info is available
        if not task.ssh_host or not task.ssh_port:
            return False

        # For mount operations, be conservative - only return True if we're
        # very confident SSH is ready. This prevents long hangs.
        # "allocated" status doesn't guarantee SSH is ready yet
        if task.status.value.lower() != "running":
            return False

        # If task was created very recently, SSH probably isn't ready
        # This is a heuristic to avoid unnecessary SSH attempts
        if hasattr(task, "created_at"):
            from datetime import datetime, timezone

            try:
                created = datetime.fromisoformat(task.created_at.replace("Z", "+00:00"))
                age_seconds = (datetime.now(timezone.utc) - created).total_seconds()
                if age_seconds < 60:  # Less than 1 minute old
                    logger.debug(
                        f"Task {task.task_id} is only {age_seconds:.0f}s old, SSH unlikely ready"
                    )
                    return False
            except:
                pass  # If we can't parse created_at, continue

        return True

    def get_capabilities(self) -> "ProviderCapabilities":
        """Get Mithril provider capabilities.

        Returns:
            ProviderCapabilities describing Mithril features
        """
        from ..base import PricingModel, ProviderCapabilities

        return ProviderCapabilities(
            # Compute capabilities
            supports_spot_instances=True,
            supports_on_demand=True,
            supports_multi_node=True,
            # Storage capabilities
            supports_attached_storage=True,
            supports_shared_storage=False,
            storage_types=["volume"],
            # Access and security
            requires_ssh_keys=True,
            supports_console_access=False,
            # Pricing and allocation
            pricing_model=PricingModel.MARKET,
            supports_reservations=False,
            # Regional capabilities
            supported_regions=SUPPORTED_REGIONS,
            cross_region_networking=False,
            # Resource limits
            max_instances_per_task=MAX_INSTANCES_PER_TASK,
            max_storage_per_instance_gb=MAX_VOLUME_SIZE_GB,
            # Advanced features
            supports_custom_images=True,
            supports_gpu_passthrough=True,
            supports_live_migration=False,
        )

    def get_remote_operations(self) -> Optional["IRemoteOperations"]:
        """Get remote operations handler for Mithril tasks.

        Returns:
            MithrilRemoteOperations instance for SSH-based remote operations
        """
        from .remote_operations import MithrilRemoteOperations

        return MithrilRemoteOperations(self)

    def resolve_instance_type(self, user_spec: str) -> str:
        """Convert user-friendly instance spec to Mithril instance type ID.

        Args:
            user_spec: User input like "a100", "4xa100", etc.

        Returns:
            Mithril instance type ID (e.g., "it_MsIRhxj3ccyVWGfP")

        Raises:
            InstanceTypeError: Invalid or unsupported spec
        """
        # Normalize the spec to lowercase
        normalized_spec = user_spec.lower().strip()

        # Check if it's already an Mithril instance ID
        if normalized_spec.startswith("it_"):
            return user_spec

        # Look up in the mappings
        if normalized_spec in self.INSTANCE_TYPE_MAPPINGS:
            return self.INSTANCE_TYPE_MAPPINGS[normalized_spec]

        # Try to parse more complex formats using the instance parser
        try:
            from flow.utils.instance_parser import parse_instance_type

            components = parse_instance_type(user_spec)

            # Build a canonical key for lookup
            if components.gpu_count > 1:
                key = f"{components.gpu_count}x{components.gpu_type}"
            else:
                key = components.gpu_type

            if key in self.INSTANCE_TYPE_MAPPINGS:
                return self.INSTANCE_TYPE_MAPPINGS[key]
        except Exception:
            pass

        # If not found, raise an error with helpful suggestions
        from flow.errors import FlowError

        available_types = list(self.INSTANCE_TYPE_MAPPINGS.keys())
        raise FlowError(
            f"Unknown instance type: '{user_spec}'",
            suggestions=[
                f"Available types: {', '.join(available_types[:5])}...",
                "Use 'flow instances' to see all available instance types",
                "Examples: 'a100', '4xa100', '8xh100'",
            ],
        )

    def parse_catalog_instance(self, instance: Instance) -> dict[str, Any]:
        """Parse Mithril instance into catalog format for GPU matching.

        Args:
            instance: Mithril instance from find_instances()

        Returns:
            Dict with standardized catalog entry format
        """
        # Extract GPU info from instance type
        gpu_type = None
        gpu_count = 0
        gpu_memory_gb = 0

        if hasattr(instance, "instance_type") and instance.instance_type:
            # Parse GPU info from instance type like "a100.80gb.sxm4.1x"
            parts = instance.instance_type.split(".")
            if len(parts) > 0:
                base_gpu = parts[0]  # e.g., "a100"

                # Extract memory if present
                if len(parts) > 1 and "gb" in parts[1].lower():
                    memory_part = parts[1].lower()
                    try:
                        gpu_memory_gb = int(memory_part.replace("gb", ""))
                        # Construct canonical gpu_type like "a100-80gb"
                        gpu_type = f"{base_gpu}-{gpu_memory_gb}gb"
                    except ValueError:
                        gpu_type = base_gpu
                else:
                    gpu_type = base_gpu

            # Extract GPU count
            if len(parts) > 3 and "x" in parts[3]:
                gpu_count = int(parts[3].replace("x", ""))  # e.g., "1x" -> 1
            else:
                gpu_count = getattr(instance, "gpu_count", 1)

        catalog_entry = {
            "name": instance.instance_type,  # _find_gpus_by_memory expects "name"
            "instance_type": instance.instance_type,
            "gpu_type": gpu_type,
            "gpu_count": gpu_count,
            "price_per_hour": instance.price_per_hour,
            "available": instance.status == "available",
        }

        # Add gpu info dict for _find_gpus_by_memory
        if gpu_type and gpu_memory_gb > 0:
            catalog_entry["gpu"] = {"model": gpu_type, "memory_gb": gpu_memory_gb}

        return catalog_entry

    # ============ Additional Mithril API Methods ============

    def get_projects(self) -> list[dict[str, Any]]:
        """Get all projects accessible to the user.

        Returns:
            List of project dictionaries
        """
        response = self.http.request(
            method="GET",
            url="/v2/projects",
        )
        return response  # API returns list directly

    def get_instance_types(self, region: str | None = None) -> list[dict[str, Any]]:
        """Get available instance types.

        Args:
            region: Optional region filter

        Returns:
            List of instance type dictionaries
        """
        params = {}
        if region:
            params["region"] = region

        response = self.http.request(
            method="GET",
            url="/v2/instance-types",
            params=params,
        )
        return response  # API returns list directly

    def get_ssh_keys(self) -> list[dict[str, Any]]:
        """Get user's SSH keys.

        Returns:
            List of SSH key dictionaries
        """
        keys = self.ssh_key_manager.list_keys()
        return [
            {
                "fid": key.fid,
                "name": key.name,
                "public_key": key.public_key,
                "created_at": key.created_at.isoformat() if key.created_at else None,
            }
            for key in keys
        ]

    def create_ssh_key(self, name: str, public_key: str) -> dict[str, Any]:
        """Create a new SSH key.

        Args:
            name: Key name
            public_key: SSH public key content

        Returns:
            Created SSH key info
        """
        key_id = self.ssh_key_manager.create_key(name, public_key)
        return {"fid": key_id, "name": name}

    def delete_ssh_key(self, key_id: str) -> bool:
        """Delete an SSH key.

        Args:
            key_id: SSH key ID

        Returns:
            True if successful
        """
        return self.ssh_key_manager.delete_key(key_id)

    # ============ Helper Methods ============

    def _build_task_from_bid(
        self,
        bid_data: dict[str, Any],
        config: TaskConfig | None = None,
        fetch_instance_details: bool = False,
    ) -> Task:
        """Build a Task object from Mithril bid data.

        Args:
            bid_data: Raw bid data from Mithril API
            config: Optional original task configuration
            fetch_instance_details: Whether to fetch full instance details (for single task lookups)

        Returns:
            Task object with all available information
        """
        # Extract basic info
        task_id = bid_data.get("fid", "")

        # Always use the actual Mithril task name for consistent resolution
        # This ensures CLI task names match exactly what Mithril/Foundry shows
        bid_name = bid_data.get("name", "")
        if bid_name:
            # Use the actual Mithril task name - this is the source of truth
            name = bid_name
        elif config and config.name:
            # Fallback to user-provided name if Mithril name is missing
            name = config.name
        else:
            # Final fallback: create identifier from task ID
            name = f"task-{task_id[:8]}" if len(task_id) > 8 else f"task-{task_id}"

        status = self._map_mithril_status_to_enum(bid_data.get("status", "pending"))

        # Parse timestamps
        created_at = (
            datetime.fromisoformat(bid_data["created_at"].replace("Z", "+00:00"))
            if bid_data.get("created_at")
            else datetime.now()
        )
        started_at = (
            datetime.fromisoformat(bid_data["started_at"].replace("Z", "+00:00"))
            if bid_data.get("started_at")
            else None
        )
        completed_at = (
            datetime.fromisoformat(bid_data["completed_at"].replace("Z", "+00:00"))
            if bid_data.get("completed_at")
            else None
        )

        # Extract resource info
        instance_type_id = bid_data.get("instance_type", "")

        # Resolve instance type to display name
        # Always use the canonical name from the instance ID to show what was actually provisioned
        if instance_type_id:
            # This will return the canonical name (e.g., "8xh100" for H100s)
            instance_type = self._get_instance_type_name(instance_type_id)
        elif config and config.instance_type:
            # Fallback to config if no instance ID available
            instance_type = config.instance_type
        else:
            instance_type = "unknown"

        num_instances = bid_data.get(
            "instance_quantity",
            bid_data.get("num_instances", config.num_instances if config else 1),
        )
        region = bid_data.get(
            "region", config.region if config else self.mithril_config.region or "unknown"
        )

        # Determine the cost per hour
        cost_per_hour = self._determine_cost_per_hour(
            bid_data, status, instance_type_id, region, fetch_instance_details
        )

        # Calculate total cost if running/completed
        total_cost = None
        if started_at and (completed_at or status == TaskStatus.RUNNING):
            duration_hours = ((completed_at or datetime.now()) - started_at).total_seconds() / 3600
            cost_value = float(cost_per_hour.strip("$"))
            total_cost = f"${duration_hours * cost_value * num_instances:.2f}"

        # Extract SSH info from instances
        ssh_host = None
        ssh_port = DEFAULT_SSH_PORT
        ssh_command = None
        instances = bid_data.get("instances", [])
        instance_created_at = None  # Track current instance creation time

        if instances and isinstance(instances, list) and instances[0]:
            first_instance = instances[0]

            # Handle both string (instance ID) and dict (full instance data) cases
            if isinstance(first_instance, str):
                if fetch_instance_details:
                    # Fetch full instance details for single task lookups
                    logger.debug(f"Fetching instance details for {first_instance}")
                    instance_data = self._fetch_instance_details(first_instance)
                    if instance_data:
                        # Replace the string ID with full instance data for status extraction
                        instances[0] = instance_data

                        ssh_destination = instance_data.get("ssh_destination")
                        if ssh_destination:
                            ssh_host, ssh_port = self._parse_ssh_destination(ssh_destination)

                        # Get instance creation time for accurate age calculation
                        if instance_data.get("created_at"):
                            try:
                                instance_created_at = datetime.fromisoformat(
                                    instance_data["created_at"].replace("Z", "+00:00")
                                )
                            except Exception as e:
                                logger.debug(f"Failed to parse instance created_at: {e}")
                else:
                    # Skip fetching instance details during list operations to avoid N+1 queries
                    logger.debug(
                        f"Skipping instance fetch for {first_instance} during list operation"
                    )

            elif isinstance(first_instance, dict):
                # Instance data included in list response
                # Check for SSH info in the instance data
                ssh_destination = first_instance.get("ssh_destination")
                if ssh_destination:
                    ssh_host, ssh_port = self._parse_ssh_destination(ssh_destination)
                else:
                    # Also check for public_ip as fallback
                    public_ip = first_instance.get("public_ip")
                    if public_ip:
                        ssh_host = public_ip
                        ssh_port = DEFAULT_SSH_PORT

                # Get instance creation time if available
                if first_instance.get("created_at"):
                    try:
                        instance_created_at = datetime.fromisoformat(
                            first_instance["created_at"].replace("Z", "+00:00")
                        )
                    except Exception as e:
                        logger.debug(f"Failed to parse instance created_at: {e}")

            # Build SSH command if we have host
            if ssh_host:
                ssh_command = f"ssh -p {ssh_port} {DEFAULT_SSH_USER}@{ssh_host}"

        # Build provider metadata
        provider_metadata = {
            "provider": "mithril",
            "bid_id": task_id,
            "bid_status": bid_data.get("status", "unknown"),
            "instance_type_id": instance_type_id,
            "limit_price": bid_data.get("limit_price"),
        }

        # Try to fetch current market price for pending bids
        if status == TaskStatus.PENDING and instance_type_id and region and fetch_instance_details:
            try:
                market_price = self._get_current_market_price(instance_type_id, region)
                if market_price:
                    provider_metadata["market_price"] = market_price

                    # Add price competitiveness analysis
                    if bid_data.get("limit_price"):
                        bid_val = self._parse_price(str(bid_data["limit_price"]))
                        if bid_val and market_price:
                            if bid_val < market_price:
                                diff = market_price - bid_val
                                provider_metadata["price_competitiveness"] = "below_market"
                                provider_metadata["price_diff"] = diff
                                provider_metadata["price_message"] = (
                                    f"Your bid is ${diff:.2f}/hour below market price"
                                )
                            elif bid_val > market_price * 1.2:
                                diff = bid_val - market_price
                                provider_metadata["price_competitiveness"] = "above_market"
                                provider_metadata["price_diff"] = diff
                                provider_metadata["price_message"] = (
                                    f"Your bid is ${diff:.2f}/hour above market price"
                                )
                            else:
                                provider_metadata["price_competitiveness"] = "at_market"
                                provider_metadata["price_message"] = (
                                    "Your bid is competitive with market price"
                                )
            except Exception as e:
                logger.debug(f"Failed to fetch market price: {e}")

        # Check instance-level status for more detailed information
        if instances and isinstance(instances, list) and instances[0]:
            first_instance = instances[0]
            if isinstance(first_instance, dict):
                instance_status = first_instance.get("status", "")
                if instance_status:
                    provider_metadata["instance_status"] = instance_status

                    # Map instance status to user-friendly messages
                    if instance_status == "STATUS_PREEMPTING":
                        provider_metadata["state_detail"] = "Instance is being preempted"
                        provider_metadata["state_help"] = (
                            "Your spot instance will be terminated soon. Save your work."
                        )
                        provider_metadata["is_preempting"] = True
                    elif instance_status in [
                        "STATUS_PENDING",
                        "STATUS_NEW",
                        "STATUS_CONFIRMED",
                        "STATUS_SCHEDULED",
                    ]:
                        provider_metadata["state_detail"] = "Instance is being allocated"
                        provider_metadata["state_help"] = (
                            "Mithril is finding available GPU resources for your bid."
                        )
                    elif instance_status in ["STATUS_INITIALIZING", "STATUS_STARTING"]:
                        provider_metadata["state_detail"] = "Instance is starting up"
                        provider_metadata["state_help"] = (
                            "Your GPU instance is booting. This typically takes 10-20 minutes."
                        )

        # Add detailed state information based on bid status
        if status == TaskStatus.PENDING and bid_data.get("status"):
            mithril_bid_status = bid_data.get("status", "")
            if mithril_bid_status == "Open":
                provider_metadata["state_detail"] = provider_metadata.get(
                    "state_detail", "Bid is open - waiting for instances"
                )
                provider_metadata["state_help"] = provider_metadata.get(
                    "state_help",
                    "Your bid is in the queue. Resources will be allocated when available at your price point.",
                )

        # Add link to Mithril spot instances console
        provider_metadata["web_console_url"] = "https://app.mithril.ai/instances/spot"

        # Build Task object
        task = Task(
            task_id=task_id,
            name=name,
            status=status,
            config=config,
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            instance_created_at=instance_created_at,
            instance_type=instance_type,
            num_instances=num_instances,
            region=region,
            cost_per_hour=cost_per_hour,
            total_cost=total_cost,
            ssh_host=ssh_host,
            ssh_port=ssh_port,
            ssh_command=ssh_command,
            instances=[
                inst.get("fid", "") if isinstance(inst, dict) else str(inst) for inst in instances
            ],
            message=bid_data.get("message"),
            provider_metadata=provider_metadata,
        )

        # Attach provider reference for method calls
        task._provider = self

        return task

    def _determine_cost_per_hour(
        self,
        bid_data: dict[str, Any],
        status: TaskStatus,
        instance_type_id: str,
        region: str,
        fetch_details: bool,
    ) -> str:
        """Determine the cost per hour for a task.

        For running/completed tasks, attempts to fetch actual market price.
        Falls back to limit price when market price unavailable.

        Args:
            bid_data: The bid data from Mithril
            status: Current task status
            instance_type_id: The instance type ID
            region: The region
            fetch_details: Whether to fetch additional details (like market price)

        Returns:
            Cost per hour as a string (e.g., "$10.00")
        """
        # For running/completed tasks, try to get actual market price
        if (
            status in [TaskStatus.RUNNING, TaskStatus.COMPLETED]
            and instance_type_id
            and region
            and fetch_details
        ):
            try:
                market_price = self._get_current_market_price(instance_type_id, region)
                if market_price:
                    return f"${market_price:.2f}"
            except Exception as e:
                logger.debug(f"Failed to get market price for {instance_type_id} in {region}: {e}")

        # Fall back to limit price from bid
        limit_price = bid_data.get("limit_price", "$0")
        return limit_price if isinstance(limit_price, str) else f"${limit_price}"

    def _get_current_market_price(self, instance_type_id: str, region: str) -> float | None:
        """Get current market price for instance type in region.

        Args:
            instance_type_id: Mithril instance type ID
            region: Region to check

        Returns:
            Current market price or None if not available
        """
        try:
            params = {"instance_type": instance_type_id, "region": region}
            auctions = self.http.request(
                method="GET",
                url="/v2/spot/availability",
                params=params,
            )

            if auctions and isinstance(auctions, list):
                # Find matching auction
                for auction in auctions:
                    if (
                        auction.get("instance_type") == instance_type_id
                        and auction.get("region") == region
                    ):
                        # Parse price
                        price_str = auction.get("last_instance_price", "")
                        return self._parse_price(price_str)

                # If no exact match, use first result
                if auctions[0]:
                    price_str = auctions[0].get("last_instance_price", "")
                    return self._parse_price(price_str)

        except Exception as e:
            logger.debug(f"Error fetching market price: {e}")

        return None

    def _map_mithril_status(self, mithril_status: str) -> str:
        """Map Mithril status to a string status.

        Args:
            mithril_status: Status string from Mithril API

        Returns:
            Mapped status string
        """
        return self._map_mithril_status_to_enum(mithril_status).value

    def _map_mithril_status_to_enum(self, mithril_status: str) -> TaskStatus:
        """Map Mithril status robustly to TaskStatus enum.

        Args:
            mithril_status: Status string from Mithril API

        Returns:
            Corresponding TaskStatus enum value
        """
        if not mithril_status:
            return TaskStatus.PENDING

        normalized = mithril_status.lower().strip()

        # Direct lookup first
        mapped_status = STATUS_MAPPINGS.get(normalized)
        if mapped_status:
            return TaskStatus[mapped_status]

        # Fuzzy matching for safety with common variations
        if "alloc" in normalized:
            return TaskStatus.RUNNING
        if "termin" in normalized or "cancel" in normalized:
            return TaskStatus.CANCELLED
        if "fail" in normalized or "error" in normalized:
            return TaskStatus.FAILED
        if "complete" in normalized or "success" in normalized:
            return TaskStatus.COMPLETED
        if "open" in normalized:
            return TaskStatus.PENDING

        logger.warning(f"Unknown Mithril status: '{mithril_status}', defaulting to PENDING")
        return TaskStatus.PENDING

    def _convert_auction_to_available_instance(
        self, auction_data: dict[str, Any]
    ) -> AvailableInstance | None:
        """Convert Mithril auction data to AvailableInstance.

        Args:
            auction_data: Raw auction data from Mithril API

        Returns:
            AvailableInstance object or None if conversion fails
        """
        try:
            # Parse price using the robust price parser
            price_str = auction_data.get("last_instance_price", auction_data.get("price", "$0"))
            price_per_hour = self._parse_price(price_str)

            # Get instance type ID from the auction data
            instance_type_id = auction_data.get(
                "instance_type", auction_data.get("instance_type_id", "")
            )

            # Try to get human-readable name
            instance_type_name = self._get_instance_type_name(instance_type_id)

            # Create AvailableInstance from auction data
            return AvailableInstance(
                allocation_id=auction_data.get("fid", auction_data.get("auction_id", "")),
                instance_type=instance_type_name,
                region=auction_data.get("region", ""),
                price_per_hour=price_per_hour,
                gpu_type=auction_data.get("gpu_type"),
                gpu_count=auction_data.get("gpu_count") or auction_data.get("num_gpus"),
                cpu_count=auction_data.get("cpu_count"),
                memory_gb=auction_data.get("memory_gb"),
                available_quantity=auction_data.get("available_gpus")
                or auction_data.get("inventory_quantity"),
                status=auction_data.get("status"),
                expires_at=(
                    datetime.fromisoformat(auction_data["expires_at"])
                    if auction_data.get("expires_at")
                    else None
                ),
                internode_interconnect=auction_data.get("internode_interconnect"),
                intranode_interconnect=auction_data.get("intranode_interconnect"),
            )
        except Exception as e:
            logger.warning(f"Failed to convert auction data: {e}")
            return None

    def _apply_instance_constraints(self, config: TaskConfig, instance_type: str) -> TaskConfig:
        """Apply Mithril-specific instance constraints to configuration.

        Args:
            config: Original task configuration
            instance_type: Requested instance type

        Returns:
            Adjusted configuration with Mithril constraints applied
        """
        # Mithril-specific constraint: H100s only come in 8-GPU nodes
        if instance_type.lower() in ["h100", "1xh100", "2xh100", "4xh100"]:
            # All H100 requests must use full 8-GPU nodes
            logger.info("Note: H100 instances only available as 8-GPU nodes on Mithril")
            # Don't modify num_instances - that's already set by the user
            # The mapping handles routing to the correct instance type

        return config

    def _resolve_instance_type_simple(self, instance_type: str) -> str:
        """Simple instance type resolution using a direct mapping.

        Args:
            instance_type: User-friendly instance type name

        Returns:
            Mithril instance type FID

        Raises:
            ValueError: If instance type is unknown
        """
        # Exact matching only - no case normalization
        normalized = instance_type.strip()

        # Direct ID passthrough
        if normalized.startswith("it_"):
            return normalized

        # Look up in provider-specific mappings
        if normalized in self.INSTANCE_TYPE_MAPPINGS:
            return self.INSTANCE_TYPE_MAPPINGS[normalized]

        # Provide helpful error with available types
        available = sorted(self.INSTANCE_TYPE_MAPPINGS.keys())
        raise ValueError(
            f"Unknown instance type: {instance_type}. Available: {', '.join(available)}"
        )

    def _is_more_specific_type(self, type1: str, type2: str) -> bool:
        """Determine if type1 is more specific than type2.

        Used to select canonical names when multiple instance types map to the same ID.
        For H100s on Mithril, we want "8xh100" since that's what Mithril actually provisions.

        Args:
            type1: First instance type name
            type2: Second instance type name

        Returns:
            True if type1 is more specific/canonical than type2
        """
        # For H100s, prefer the simple "8xh100" format for clear GPU counting
        if "h100" in type1.lower() and "h100" in type2.lower():
            # Prefer "8xh100" format over others for consistency
            if type1.lower() == "8xh100":
                return True
            if type2.lower() == "8xh100":
                return False

        # Extract GPU count if present
        import re

        match1 = re.match(r"(\d+)x(.+)", type1.lower())
        match2 = re.match(r"(\d+)x(.+)", type2.lower())

        # If only one has explicit count, prefer that one
        if match1 and not match2:
            return True
        if match2 and not match1:
            return False

        # If both have counts, prefer higher count (actual provisioned config)
        if match1 and match2:
            count1 = int(match1.group(1))
            count2 = int(match2.group(1))
            if count1 != count2:
                return count1 > count2

        # Default: maintain existing order
        return False

    def _get_instance_type_name(self, instance_id: str) -> str:
        """Get human-readable name for instance type ID.

        Args:
            instance_id: Mithril instance type FID

        Returns:
            User-friendly display name
        """
        # Build reverse mapping for display, preferring canonical names
        # For IDs with multiple mappings, use the canonical (most specific) form
        canonical_reverse_mappings = {}
        for name, id_value in self.INSTANCE_TYPE_MAPPINGS.items():
            # Prefer more specific names (e.g., "8xh100" over "h100")
            if id_value not in canonical_reverse_mappings or self._is_more_specific_type(
                name, canonical_reverse_mappings[id_value]
            ):
                canonical_reverse_mappings[id_value] = name

        # Try exact match first
        if instance_id in canonical_reverse_mappings:
            return canonical_reverse_mappings[instance_id]

        # For unknown IDs, try to extract meaningful info
        # Some IDs might contain GPU hints in their structure
        instance_upper = instance_id.upper()

        # Common GPU patterns to look for
        gpu_patterns = [
            ("A100", ["A100", "AMPERE"]),
            ("H100", ["H100", "HOPPER"]),
            ("A10", ["A10"]),
            ("V100", ["V100", "VOLTA"]),
            ("T4", ["T4", "TURING"]),
            ("L4", ["L4"]),
            ("A40", ["A40"]),
        ]

        for gpu_name, patterns in gpu_patterns:
            if any(pattern in instance_upper for pattern in patterns):
                return f"GPU-{gpu_name}"

        # If it's an Mithril ID format but unknown, return a cleaner version
        if instance_id.startswith(("it_", "IT_")):
            # Return just "GPU" for unknown instance types
            # This is cleaner than showing internal IDs to users
            return "GPU"

        # Last resort - return the original
        return instance_id

    def _get_instance_display_name(self, instance_id: str) -> str:
        """Alias for _get_instance_type_name for compatibility.

        Args:
            instance_id: Mithril instance type FID

        Returns:
            Human-readable name or the ID if not found
        """
        return self._get_instance_type_name(instance_id)

    def _fetch_instance_details(self, instance_id: str) -> dict[str, Any] | None:
        """Fetch instance details from API.

        Args:
            instance_id: Mithril instance ID (e.g., 'ins_...')

        Returns:
            Instance data dictionary or None if not found
        """
        try:
            project_id = self._get_project_id()
            response = self.http.request(
                method="GET",
                url="/v2/instances",
                params={"fid": instance_id, "project": project_id},
            )
            instances = response.get("data", [])
            # Find the instance with matching ID
            for inst in instances:
                if inst.get("fid") == instance_id:
                    return inst
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch instance {instance_id}: {e}")
            return None

    def _parse_ssh_destination(self, ssh_destination: str | None) -> tuple[str | None, int]:
        """Parse ssh_destination field into host and port.

        Args:
            ssh_destination: SSH destination string (e.g., "host:port" or "host")

        Returns:
            Tuple of (host, port) where port defaults to 22
        """
        if not ssh_destination:
            return None, 22

        # ssh_destination might be "host:port" or just "host"
        parts = ssh_destination.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 22
        return host, port

    def _check_availability(self, instance_type: str) -> dict[str, Auction]:
        """Check instance availability across all regions.

        Args:
            instance_type: User-friendly instance type (e.g., "a100", "4xa100")

        Returns:
            Dict mapping region to best auction in that region
        """
        # Resolve instance type to FID
        try:
            instance_fid = self._resolve_instance_type(instance_type)
        except MithrilInstanceError:
            logger.warning(f"Unknown instance type: {instance_type}")
            return {}

        # Query spot availability API with retry logic
        try:

            @with_retry(
                max_attempts=3,
                initial_delay=0.5,
                retriable_exceptions=(NetworkError, TimeoutError, HTTPError),
            )
            def _get_availability():
                return self._circuit_breaker.call(
                    lambda: self.http.request(
                        method="GET",
                        url="/v2/spot/availability",
                    )
                )

            response = _get_availability()
            auctions = response  # API returns list directly
        except Exception as e:
            logger.warning(f"Failed to check availability: {e}")
            return {}

        # Filter by instance type and group by region
        availability_by_region = {}
        for auction_data in auctions:
            # Check if this auction matches our instance type
            if auction_data.get("instance_type") != instance_fid:
                continue

            region = auction_data.get("region")
            if not region:
                continue

            # Convert to Auction object
            auction = Auction(
                fid=auction_data.get("fid"),
                instance_type=auction_data.get("instance_type"),
                region=region,
                capacity=auction_data.get("capacity", 0),
                last_instance_price=auction_data.get("last_instance_price", "$0"),
            )

            # Keep best (cheapest) auction per region
            auction_price = self._parse_price(auction.last_instance_price)
            if region not in availability_by_region:
                availability_by_region[region] = auction
            else:
                existing_price = self._parse_price(
                    availability_by_region[region].last_instance_price
                )
                if auction_price < existing_price:
                    availability_by_region[region] = auction

        return availability_by_region

    def _select_best_region(
        self, availability: dict[str, Auction], preferred_region: str | None = None
    ) -> str | None:
        """Select best region based on availability and preferences.

        Args:
            availability: Dict of region -> Auction
            preferred_region: User's preferred region (if any)

        Returns:
            Selected region or None if no availability
        """
        if not availability:
            return None

        # If user specified a region and it's available, use it
        if preferred_region and preferred_region in availability:
            return preferred_region

        # Otherwise, select based on:
        # 1. Highest capacity (most GPUs available)
        # 2. Lowest price
        best_region = None
        best_score = (-1, float("inf"))  # (capacity, price)

        for region, auction in availability.items():
            capacity = auction.capacity or 0
            price = self._parse_price(auction.last_instance_price)
            score = (capacity, price)
            # Higher capacity is better, lower price is better
            if score[0] > best_score[0] or (score[0] == best_score[0] and score[1] < best_score[1]):
                best_score = score
                best_region = region

        return best_region

    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float.

        Args:
            price_str: Price string (e.g., "$10.00")

        Returns:
            Price as float
        """
        if not price_str:
            return 0.0

        # Remove $ sign, commas, and any whitespace
        clean_price = price_str.strip().lstrip("$").replace(",", "").strip()

        try:
            return float(clean_price)
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse price: {price_str}")
            return 0.0

    def get_init_interface(self) -> "IProviderInit":
        """Get provider initialization interface.

        Returns:
            IProviderInit implementation for Mithril provider
        """
        from .init import MithrilInit

        return MithrilInit(self.http)

    def _is_price_validation_error(self, error: ValidationAPIError) -> bool:
        """Check if a validation error is related to insufficient bid price.

        Args:
            error: The validation error to check

        Returns:
            True if this is a price-related validation error
        """
        if not hasattr(error, "validation_errors") or not error.validation_errors:
            return False

        # Check for price-related error messages
        price_keywords = ["price", "bid", "limit_price", "minimum", "insufficient"]

        for validation_error in error.validation_errors:
            msg = validation_error.get("msg", "").lower()
            field = validation_error.get("loc", [])

            # Check if field name indicates price
            if field and any("price" in str(f).lower() for f in field):
                return True

            # Check if error message indicates price issue
            if any(keyword in msg for keyword in price_keywords):
                return True

        return False

    def _enhance_price_error(
        self,
        error: ValidationAPIError,
        instance_type_id: str,
        region: str,
        attempted_price: float | None,
    ) -> InsufficientBidPriceError:
        """Enhance a price validation error with current market pricing.

        Args:
            error: The original validation error
            instance_type_id: Mithril instance type ID
            region: Region where bid was attempted
            attempted_price: The price that was rejected

        Returns:
            Enhanced error with pricing recommendations
        """
        try:
            # Query current spot availability for this instance type
            params = {"instance_type": instance_type_id, "region": region}

            auctions = self.http.request(
                method="GET",
                url="/v2/spot/availability",
                params=params,
            )

            if not auctions:
                # No availability data, return original error
                raise error

            # Find the auction for this specific region/instance
            auction = auctions[0] if len(auctions) == 1 else None
            if not auction:
                # Try to find matching auction
                for a in auctions:
                    if a.get("region") == region and a.get("instance_type") == instance_type_id:
                        auction = a
                        break

            if not auction:
                # Still no match, use first available
                auction = auctions[0]

            # Extract pricing information
            last_price_str = auction.get("last_instance_price", "")
            min_bid_str = auction.get("min_bid_price", "")

            # Parse prices
            current_price = self._parse_price(last_price_str) if last_price_str else None
            min_bid_price = self._parse_price(min_bid_str) if min_bid_str else None

            # Use the higher of current price or minimum bid
            effective_price = max(filter(None, [current_price, min_bid_price]), default=None)

            if effective_price:
                # Calculate recommended price (50% above current)
                recommended_price = effective_price * 1.5

                # Get human-readable instance type name
                instance_name = self._get_instance_type_name(instance_type_id)

                # Create enhanced error message
                message = (
                    f"Bid price ${attempted_price:.2f}/hour is too low for {instance_name} in {region}. "
                    f"Current spot price is ${effective_price:.2f}/hour."
                )

                return InsufficientBidPriceError(
                    message=message,
                    current_price=effective_price,
                    min_bid_price=min_bid_price,
                    recommended_price=recommended_price,
                    instance_type=instance_name,
                    region=region,
                    response=getattr(error, "response", None),
                )

        except Exception as e:
            # If we fail to enhance the error, log and return original
            logger.warning(f"Failed to enhance price error: {e}")

        # Return original error if enhancement fails
        raise error

    def close(self):
        """Clean up resources."""
        self.http.close()
