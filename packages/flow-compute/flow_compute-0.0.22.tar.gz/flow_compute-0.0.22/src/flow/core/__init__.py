"""Core package for Flow engine and provider setup.

This module avoids importing heavy submodules at import time to prevent
initialization-order cycles (e.g., when `flow.api.models` imports a light
utility like `flow.core.docker`).

Symbols are lazily imported via __getattr__ on first access.
"""

__all__ = [
    # Task engine
    "TaskEngine",
    "TaskProgress",
    "ResourceTracker",
    "TrackedResource",
    "TrackedVolume",
    "TrackedInstance",
    "run_task",
    "monitor_task",
    "wait_for_task",
    # Provider setup
    "ProviderSetup",
    "SetupResult",
    "SetupRegistry",
    "register_providers",
    # Paths/constants (lightweight; safe to expose)
    "WORKSPACE_DIR",
    "VOLUMES_ROOT",
    "DATA_ROOT",
    "EPHEMERAL_NVME_DIR",
    "DEV_HOME_DIR",
    "DEV_ENVS_ROOT",
    "RESULT_FILE",
    "STARTUP_SCRIPT_PREFIX",
    "S3FS_CACHE_DIR",
    "S3FS_PASSWD_FILE",
    # Helpers
    "default_volume_mount_path",
    "auto_target_for_source",
]


def __getattr__(name: str):
    if name in {
        "TaskEngine",
        "TaskProgress",
        "ResourceTracker",
        "TrackedResource",
        "TrackedVolume",
        "TrackedInstance",
        "run_task",
        "monitor_task",
        "wait_for_task",
    }:
        from flow.core.task_engine import (
            TaskEngine,
            TaskProgress,
            ResourceTracker,
            TrackedResource,
            TrackedVolume,
            TrackedInstance,
            run_task,
            monitor_task,
            wait_for_task,
        )
        return locals()[name]
    if name in {"ProviderSetup", "SetupResult"}:
        from flow.core.provider_setup import ProviderSetup, SetupResult
        return locals()[name]
    if name in {"SetupRegistry", "register_providers"}:
        from flow.core.setup_registry import SetupRegistry, register_providers
        return locals()[name]
    if name in {
        # Path constants
        "WORKSPACE_DIR",
        "VOLUMES_ROOT",
        "DATA_ROOT",
        "EPHEMERAL_NVME_DIR",
        "DEV_HOME_DIR",
        "DEV_ENVS_ROOT",
        "RESULT_FILE",
        "STARTUP_SCRIPT_PREFIX",
        "S3FS_CACHE_DIR",
        "S3FS_PASSWD_FILE",
        # Helpers
        "default_volume_mount_path",
    }:
        from flow.core.paths import (
            WORKSPACE_DIR,
            VOLUMES_ROOT,
            DATA_ROOT,
            EPHEMERAL_NVME_DIR,
            DEV_HOME_DIR,
            DEV_ENVS_ROOT,
            RESULT_FILE,
            STARTUP_SCRIPT_PREFIX,
            S3FS_CACHE_DIR,
            S3FS_PASSWD_FILE,
            default_volume_mount_path,
        )
        return locals()[name]
    if name in {"auto_target_for_source"}:
        from flow.core.mount_rules import auto_target_for_source
        return locals()[name]
    raise AttributeError(name)
