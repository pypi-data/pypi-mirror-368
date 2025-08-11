## Flow Providers Refactor: SOLID, Composition, and Google Style Compliance

### Context and Goals

This document proposes a provider-layer refactor that:

- Aligns implementations with SOLID principles, emphasizes composition over inheritance, and standardizes interfaces.
- Preserves the existing public `IProvider` API while improving testability and maintainability.
- Enforces Google Python Style Guide for docstrings, naming, and function sizing across provider modules.

Targets primarily `src/flow/providers/mithril/provider.py`, generalizing the pattern across all providers.

### Problems Observed (Today)

- Large, monolithic provider class (hundreds of lines) with mixed concerns: bidding, pricing, region selection, logging, SSH, volumes, code upload, script prep, caching.
- Tight coupling to HTTP and startup script details; hard to test in isolation.
- Inconsistent caching and retry semantics sprinkled throughout the class.
- Public method surface outgrows core protocols, making it harder to reason about what’s guaranteed vs. provider-specific.

### Design Principles

- Single Responsibility: small services/modules with one reason to change.
- Open/Closed: introduce new behavior via strategies, not by editing the facade.
- Liskov Substitution: facades conform to `IProvider` protocols and remain substitutable.
- Interface Segregation: providers implement the combined `IProvider`, while internal services expose minimal APIs.
- Dependency Inversion: provider composes services via constructor injection; core depends on abstractions.

Google Python Style Guide:

- Complete Google-style docstrings on all public functions and classes.
- Descriptive names, explicit types, small functions, clear exceptions.
- Consistent imports and logging practices; avoid overly clever code.

### Target Architecture Overview

Provider becomes a thin facade composed of small services (composition over inheritance). Strategies are used where behavior needs to vary (script transfer, region selection, code upload, pricing source).

```mermaid
graph TD
  A[MithrilProvider (Facade)] --> B[ApiClient]
  A --> C[BidService]
  A --> D[TaskService]
  A --> E[InstanceService]
  A --> F[VolumeService]
  A --> G[RegionSelector]
  A --> H[PricingService]
  A --> I[ScriptPreparationService]
  A --> J[CodeUploadService]
  A --> K[LogService]
  A --> L[SSHKeyResolver]
  A --> M[TtlCache (users, logs)]

  I --> I1[IScriptTransferStrategy]
  J --> J1[ICodeUploadStrategy]
  G --> G1[IRegionSelectionPolicy]
  H --> H1[IPricingSource]
```

### Module Organization (Mithril example)

- `providers/mithril/provider.py`: thin facade only; delegates to services
- `providers/mithril/api/`
  - `client.py`: low-level HTTP wrappers for bids, instances, volumes, users
  - `dto.py`: lightweight pydantic models for raw payloads
- `providers/mithril/domain/`
  - `bids.py`: bid submission/query and price-related error enhancement
  - `tasks.py`: Task construction, status mapping, instance-type display
  - `instances.py`: instance fetch and normalization
  - `volumes.py`: volume CRUD, attach/mount orchestration
  - `pricing.py`: price parsing and current/minimum price lookups
  - `region.py`: availability gathering and region selection policy
  - `ssh_keys.py`: SSH key resolution and generation workflows
  - `logs.py`: `get_task_logs` and `stream_task_logs` via `IRemoteOperations`
  - `script_prep.py`: startup script building and size strategy orchestration
  - `code_upload.py`: code upload strategies and background sync orchestration
  - `mounts.py`: adapt Flow mounts to provider volumes + environment
  - `caches.py`: small TTL caches (users, logs) with size caps
- `providers/mithril/adapters/` (keep): conversions to `flow.api.models`
- `providers/mithril/runtime/` (keep): startup builder and related utilities
- `providers/mithril/errors/` (keep): provider-specific error taxonomy

### Service Responsibilities (SRP)

- ApiClient: wraps `IHttpClient` and centralizes base_url, headers, retry/circuit-breaker usage.
- BidService: build bid specification, POST bids, extract IDs, list bids.
- TaskService: construct `Task` from bid data; enrich with instance details when needed.
- InstanceService: fetch single/multiple instance details; normalize SSH info.
- VolumeService: create/delete/list volumes; attach/mount flows with safety checks.
- PricingService: parse/stringify prices; fetch current and min bid prices; advise recommended bid.
- RegionSelector: check cross-region availability and select best region by capacity/price policy.
- ScriptPreparationService: build and prepare startup script; choose strategy; report limits.
- CodeUploadService: pick upload strategy (rsync/scp/none); orchestrate background upload.
- LogService: cache-aware log retrieval and streaming via `IRemoteOperations`.
- SSHKeyResolver: resolve platform and local SSH keys; auto-generate as needed.
- Caches: two TTL caches with max size; shared policy for eviction.

### Public API Surface (Compatibility)

The provider facade continues to implement `flow.core.provider_interfaces.IProvider` and its parents. Required methods retained with same signatures:

- Compute:
  - `normalize_instance_request(gpu_count, gpu_type=None) -> tuple[str, int, str|None]`
  - `find_instances(requirements: dict[str, Any], limit: int = 10) -> list[AvailableInstance]`
  - `submit_task(instance_type: str, config: TaskConfig, volume_ids: list[str] | None = None, ...) -> Task`
  - `prepare_task_config(config: TaskConfig) -> TaskConfig`
  - `get_task(task_id: str) -> Task`
  - `get_task_status(task_id: str) -> TaskStatus`
  - `stop_task(task_id: str) -> bool` (and `cancel_task` as alias)
  - `get_task_logs(task_id: str, tail: int = 100, log_type: str = "stdout") -> str`
  - `stream_task_logs(task_id: str, log_type: str = "stdout") -> Iterator[str]`
  - `list_tasks(status: TaskStatus | None = None, limit: int = 100, ...) -> list[Task]`
  - `get_task_instances(task_id: str) -> list[Instance]`

- Storage:
  - `create_volume(size_gb: int, name: str | None = None, interface: str = "block") -> Volume`
  - `delete_volume(volume_id: str) -> bool`
  - `list_volumes(limit: int = 100) -> list[Volume]`
  - `upload_file(volume_id: str, local_path: Path, remote_path: str | None = None) -> bool`
  - `upload_directory(volume_id: str, local_path: Path, remote_path: str | None = None) -> bool`
  - `download_file(volume_id: str, remote_path: str, local_path: Path) -> bool`
  - `download_directory(volume_id: str, remote_path: str, local_path: Path) -> bool`
  - `is_volume_id(identifier: str) -> bool`

- Cross-cutting:
  - `get_remote_operations() -> IRemoteOperations | None`
  - `resolve_instance_type(user_spec: str) -> str`
  - `get_user(user_id: str) -> User`
  - `get_capabilities() -> ProviderCapabilities`

Provider-specific extension methods remain, but are explicitly documented as extensions and not required by `IProvider`:

- `list_active_tasks(limit: int = 100) -> list[Task]`
- `mount_volume(volume_id: str, task_id: str, mount_point: str | None = None) -> None`
- `get_projects() -> list[dict[str, Any]]`
- `get_instance_types(region: str | None = None) -> list[dict[str, Any]]`
- `get_ssh_keys() -> list[dict[str, Any]]`, `create_ssh_key(...)`, `delete_ssh_key(...)`
- `get_init_interface() -> IProviderInit`
- `get_ssh_tunnel_manager()`
- `close() -> None`

If desired, these can be formalized via optional extension Protocols (e.g., `IMithrilExtensions`) to make capabilities discoverable without RTTI.

### Composition Over Inheritance

- The facade composes services; internal classes are plain objects; strategies implement small Protocols.
- No subclassing of the facade; behavior variance is injected via strategy and policy objects (`IScriptTransferStrategy`, `ICodeUploadStrategy`, `IRegionSelectionPolicy`, `IPricingSource`).
- Adapters remain simple conversion utilities, not base classes.

This uses composition over inheritance in the right places: behavior is swapped by composition, while the public type (`IProvider`) remains stable.

### Error Handling, Retries, and Circuit Breaker

- Centralize retry and circuit-breaker logic in ApiClient wrappers; services call ApiClient methods.
- Validation and domain-specific errors are mapped in services (e.g., price validation in `PricingService`).
- Keep idempotent operations for pause/unpause; ensure clear error messages and suggestions.

### Caching

- Replace ad-hoc dict caches with a shared `TtlCache` helper in `domain/caches.py` with:
  - ttl_seconds, max_entries, and simple LRU-with-expiration behavior.
  - Used by LogService and User resolution paths.

### Dependency Injection and Configuration

- `MithrilProvider.from_config(config)` continues to build the pooled HTTP client and wire default services.
- Constructors accept optional overrides for any service to simplify testing and customization.

### Testing Strategy

- Unit tests per service with mocked ApiClient.
- Strategy tests for script prep thresholds and code upload decisions.
- Region selection policy tests (capacity-first, price tie-break).
- Volume attach/mount tests (region mismatch, multi-instance restrictions).
- Log service tests (pending/cancelled/running branches and SSH failures).
- SSH key resolver tests (env var, platform keys, common local defaults).

### Migration Plan (Incremental PRs)

1) Extract `api/client.py` and `domain/pricing.py`; move pricing helpers and raw API calls.
2) Extract `domain/region.py` and `domain/tasks.py` (availability/selection and task construction).
3) Extract `domain/logs.py` and `domain/instances.py`; wire facade to use them.
4) Extract `domain/script_prep.py` and `domain/code_upload.py` with strategies; keep defaults.
5) Extract `domain/volumes.py` and mount operations.
6) Introduce `domain/caches.py`; replace `_user_cache`/`_log_cache` usage.
7) Enable Google docstring lint (optional) and fix visible docstrings.
8) Add/expand tests for all services.

### Style and Tooling (Optional Enhancements)

- Enable Google docstring checks in Ruff:

  - Add to `pyproject.toml`:

    - `[tool.ruff.lint]` `select += ["D"]`
    - `[tool.ruff.lint.pydocstyle]` `convention = "google"`

- Consider `ANN` rule set for public API type hints; keep line-length 100 to match Black.

### Risks and Mitigations

- Behavior drift during extraction: mitigate with high-coverage unit tests and incremental PRs.
- Hidden coupling to CLI/UX: preserve method signatures and return types; stage changes behind the facade.
- Team learning curve: document service responsibilities and examples here; add code owner reviews for provider modules.

### Public API Compliance Checklist

- Facade methods exactly match `IProvider` protocols in `flow/core/provider_interfaces.py`.
- Provider-specific extras remain opt-in and documented; optionally model via extension Protocols.
- No breaking changes in method names, parameters, or return types; migrations are internal only.

### Open Questions

- Do we want to formalize provider-specific extensions via optional Protocols and advertise via registry metadata?
- Should we standardize mount operations (like `mount_volume`) into `IStorageProvider` or keep as an extension?


