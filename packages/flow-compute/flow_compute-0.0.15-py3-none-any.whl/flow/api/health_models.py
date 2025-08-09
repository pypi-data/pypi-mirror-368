"""Health monitoring data models for Flow SDK.

This module defines the data structures used for GPU and system health monitoring,
designed to work with GPUd metrics and provide a clean API for health analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class HealthStatus(str, Enum):
    """Overall health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentHealth(str, Enum):
    """Individual component health states."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class GPUProcess:
    """GPU process information."""

    pid: int
    name: str
    memory_mb: int
    gpu_index: int


@dataclass
class GPUMetric:
    """Comprehensive GPU metrics from GPUd."""

    gpu_index: int
    uuid: str
    name: str
    temperature_c: float
    power_draw_w: float
    power_limit_w: float
    memory_used_mb: int
    memory_total_mb: int
    gpu_utilization_pct: float
    sm_occupancy_pct: float
    clock_mhz: int
    max_clock_mhz: int
    ecc_errors: int = 0
    xid_events: List[str] = field(default_factory=list)
    nvlink_status: str = "healthy"
    processes: List[GPUProcess] = field(default_factory=list)

    @property
    def memory_utilization_pct(self) -> float:
        """Calculate memory utilization percentage."""
        if self.memory_total_mb == 0:
            return 0.0
        return (self.memory_used_mb / self.memory_total_mb) * 100

    @property
    def power_utilization_pct(self) -> float:
        """Calculate power utilization percentage."""
        if self.power_limit_w == 0:
            return 0.0
        return (self.power_draw_w / self.power_limit_w) * 100

    @property
    def is_throttling(self) -> bool:
        """Check if GPU is throttling."""
        return self.clock_mhz < self.max_clock_mhz * 0.9


@dataclass
class SystemMetrics:
    """System-level metrics."""

    cpu_usage_pct: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage_pct: float
    network_rx_mbps: float = 0.0
    network_tx_mbps: float = 0.0
    open_file_descriptors: int = 0
    load_average: List[float] = field(default_factory=list)

    @property
    def memory_utilization_pct(self) -> float:
        """Calculate memory utilization percentage."""
        if self.memory_total_gb == 0:
            return 0.0
        return (self.memory_used_gb / self.memory_total_gb) * 100


@dataclass
class HealthState:
    """Health check state from GPUd."""

    component: str
    health: ComponentHealth
    message: str
    severity: str = "info"
    timestamp: Optional[datetime] = None


@dataclass
class SystemEvent:
    """System event (error, warning, info)."""

    timestamp: datetime
    component: str
    level: str  # error, warning, info
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeHealthSnapshot:
    """Complete health snapshot for a node."""

    # Identity
    task_id: str
    task_name: str
    instance_id: str
    instance_type: str
    timestamp: datetime

    # GPUd status
    gpud_healthy: bool
    gpud_version: Optional[str] = None

    # Machine info from GPUd /machine-info
    machine_info: Dict[str, Any] = field(default_factory=dict)

    # Metrics
    gpu_metrics: List[GPUMetric] = field(default_factory=list)
    system_metrics: Optional[SystemMetrics] = None

    # Health states from GPUd /v1/states
    health_states: List[HealthState] = field(default_factory=list)

    # Events from GPUd /v1/events
    events: List[SystemEvent] = field(default_factory=list)

    # Computed health
    health_score: float = 1.0
    health_status: HealthStatus = HealthStatus.UNKNOWN

    @property
    def gpu_count(self) -> int:
        """Number of GPUs on this node."""
        return len(self.gpu_metrics)

    @property
    def has_critical_events(self) -> bool:
        """Check if there are any critical events."""
        return any(e.level == "error" for e in self.events)

    @property
    def unhealthy_components(self) -> List[str]:
        """List of unhealthy components."""
        return [
            state.component
            for state in self.health_states
            if state.health in (ComponentHealth.UNHEALTHY, ComponentHealth.DEGRADED)
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "instance_id": self.instance_id,
            "instance_type": self.instance_type,
            "timestamp": self.timestamp.isoformat(),
            "gpud_healthy": self.gpud_healthy,
            "gpud_version": self.gpud_version,
            "machine_info": self.machine_info,
            "gpu_metrics": [
                {
                    "gpu_index": g.gpu_index,
                    "uuid": g.uuid,
                    "name": g.name,
                    "temperature_c": g.temperature_c,
                    "power_draw_w": g.power_draw_w,
                    "power_limit_w": g.power_limit_w,
                    "memory_used_mb": g.memory_used_mb,
                    "memory_total_mb": g.memory_total_mb,
                    "gpu_utilization_pct": g.gpu_utilization_pct,
                    "sm_occupancy_pct": g.sm_occupancy_pct,
                    "clock_mhz": g.clock_mhz,
                    "max_clock_mhz": g.max_clock_mhz,
                    "ecc_errors": g.ecc_errors,
                    "xid_events": g.xid_events,
                    "nvlink_status": g.nvlink_status,
                    "processes": [
                        {
                            "pid": p.pid,
                            "name": p.name,
                            "memory_mb": p.memory_mb,
                            "gpu_index": p.gpu_index,
                        }
                        for p in g.processes
                    ],
                }
                for g in self.gpu_metrics
            ],
            "system_metrics": {
                "cpu_usage_pct": self.system_metrics.cpu_usage_pct,
                "memory_used_gb": self.system_metrics.memory_used_gb,
                "memory_total_gb": self.system_metrics.memory_total_gb,
                "disk_usage_pct": self.system_metrics.disk_usage_pct,
                "network_rx_mbps": self.system_metrics.network_rx_mbps,
                "network_tx_mbps": self.system_metrics.network_tx_mbps,
                "open_file_descriptors": self.system_metrics.open_file_descriptors,
                "load_average": self.system_metrics.load_average,
            }
            if self.system_metrics
            else None,
            "health_states": [
                {
                    "component": s.component,
                    "health": s.health.value,
                    "message": s.message,
                    "severity": s.severity,
                    "timestamp": s.timestamp.isoformat() if s.timestamp else None,
                }
                for s in self.health_states
            ],
            "events": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "component": e.component,
                    "level": e.level,
                    "message": e.message,
                    "details": e.details,
                }
                for e in self.events
            ],
            "health_score": self.health_score,
            "health_status": self.health_status.value,
        }


@dataclass
class FleetHealthSummary:
    """Summary of health across all nodes."""

    timestamp: datetime
    total_nodes: int
    healthy_nodes: int
    degraded_nodes: int
    critical_nodes: int

    # Aggregate metrics
    total_gpus: int
    healthy_gpus: int
    avg_gpu_temperature: float
    avg_gpu_utilization: float
    avg_gpu_memory_utilization: float

    # Top issues
    critical_issues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)

    # Legacy nodes (without GPUd monitoring)
    legacy_nodes: int = 0

    @property
    def health_percentage(self) -> float:
        """Overall fleet health percentage."""
        if self.total_nodes == 0:
            return 0.0
        return (self.healthy_nodes / self.total_nodes) * 100

    @property
    def has_critical_issues(self) -> bool:
        """Check if fleet has any critical issues."""
        return self.critical_nodes > 0 or len(self.critical_issues) > 0


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""

    component: str
    status: str  # pass, fail, warning
    message: str
    details: Optional[str] = None
    suggestion: Optional[str] = None
