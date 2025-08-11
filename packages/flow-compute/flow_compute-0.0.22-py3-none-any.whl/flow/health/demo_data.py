"""Demo health data generation utilities.

Generates schema-accurate, realistic GPU/system health snapshots for demo mode
without coupling to the real health-checking logic or networking code.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import random
from typing import Any, Iterable

from flow.api.health_models import (
    ComponentHealth,
    FleetHealthSummary,
    GPUMetric,
    GPUProcess,
    HealthState,
    HealthStatus,
    NodeHealthSnapshot,
    SystemEvent,
    SystemMetrics,
)


def select_demo_scenarios(tasks: list[Any]) -> dict[str, str]:
    """Return a mapping of task_id to scenario ('healthy'|'degraded').

    Policy: all healthy except one degraded, stable across runs.
    """
    if not tasks:
        return {}
    # Deterministic choice based on concatenated IDs
    ids = "|".join(t.task_id for t in tasks)
    seed = int(hashlib.md5(ids.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    idx = rng.randrange(0, len(tasks))
    mapping: dict[str, str] = {t.task_id: "healthy" for t in tasks}
    mapping[tasks[idx].task_id] = "degraded"
    return mapping


def generate_demo_snapshot(task: Any, scenario: str = "healthy") -> NodeHealthSnapshot:
    """Generate a realistic NodeHealthSnapshot for demo purposes.

    Values are deterministic per-task for stability, and constrained to
    physically plausible ranges for modern datacenter GPUs.
    """
    seed_int = int(hashlib.md5((task.task_id or task.name or "").encode()).hexdigest()[:8], 16)
    rng = random.Random(seed_int)

    # Small node-level jitter to avoid repeated integers across nodes
    node_jitter = rng.uniform(-0.03, 0.03)

    # Infer GPU count heuristically from instance_type naming
    gpu_count = 4
    try:
        it = (task.instance_type or "").lower()
        if any(x in it for x in ["8x", "x8", "8g", "8gpu"]):
            gpu_count = 8
        elif any(x in it for x in ["2x", "x2", "2g", "2gpu"]):
            gpu_count = 2
        elif any(x in it for x in ["1x", "x1", "1g", "1gpu"]):
            gpu_count = 1
    except Exception:
        pass

    gpu_name = rng.choice(["NVIDIA A100 80GB", "NVIDIA H100 80GB", "NVIDIA L4"])
    mem_total = 81920 if ("100" in gpu_name or "A100" in gpu_name) else 24576
    power_limit = 300 if ("100" in gpu_name or "A100" in gpu_name) else 120
    max_clock = 1410 if ("100" in gpu_name or "A100" in gpu_name) else 1530

    gpu_metrics: list[GPUMetric] = []
    for idx in range(gpu_count):
        base = rng.random()
        if scenario == "healthy":
            utilization = 40 + base * 45  # 40-85%
            temp = 55 + base * 17  # 55-72°C
            ecc = 0
            xid: list[str] = []
        elif scenario == "degraded":
            utilization = 70 + base * 25  # 70-95%
            temp = 77 + base * 8  # 77-85°C
            ecc = 0 if base < 0.8 else 1
            xid = []
        else:  # critical (not used by default in demo)
            utilization = 85 + base * 15
            temp = 82 + base * 8
            ecc = 1 if base < 0.6 else 2
            xid = ["Xid 79"] if base < 0.5 else ["Xid 13"]

        # Apply node-level jitter
        utilization = max(0.0, min(100.0, utilization * (1.0 + node_jitter)))
        temp = max(30.0, temp + node_jitter * 2.0)

        # Memory utilization: healthy is broad, degraded tightened to 70–80%
        if scenario == "degraded":
            mem_frac = 0.70 + base * 0.10
        elif scenario == "healthy":
            mem_frac = 0.45 + base * 0.30
        else:
            mem_frac = 0.80 + base * 0.15
        mem_frac = max(0.0, min(0.98, mem_frac * (1.0 + node_jitter)))
        mem_used = int(mem_frac * mem_total)

        # Power and clocks correlate with utilization/thermals
        power_draw = min(power_limit, round((0.45 + (utilization / 100) * 0.55) * power_limit, 1))
        clock = int((0.88 + (utilization / 100) * 0.12) * max_clock)

        # Explicit thermal cap behavior
        if temp >= 83.0:
            clock = int(0.85 * max_clock)
            power_draw = max(power_draw, int(0.92 * power_limit))

        # Processes
        processes: list[GPUProcess] = []
        proc_count = 1 + int(base * 3)
        remaining = mem_used
        for p in range(proc_count):
            if p == proc_count - 1:
                mem_p = max(128, remaining // 2)
            else:
                mem_p = max(128, int(remaining * (0.2 + rng.random() * 0.4)))
            remaining = max(0, remaining - mem_p)
            processes.append(
                GPUProcess(
                    pid=10000 + idx * 100 + p,
                    name=rng.choice(["python", "torchrun", "trainer", "inference-server"]),
                    memory_mb=mem_p,
                    gpu_index=idx,
                )
            )

        gpu_metrics.append(
            GPUMetric(
                gpu_index=idx,
                uuid=f"GPU-{idx}-{task.task_id[:8]}",
                name=gpu_name,
                temperature_c=temp,
                power_draw_w=power_draw,
                power_limit_w=power_limit,
                memory_used_mb=mem_used,
                memory_total_mb=mem_total,
                gpu_utilization_pct=utilization,
                sm_occupancy_pct=max(0.0, min(100.0, utilization - 5 + rng.random() * 10)),
                clock_mhz=clock,
                max_clock_mhz=max_clock,
                ecc_errors=ecc,
                xid_events=xid,
                nvlink_status="healthy" if scenario != "critical" else ("degraded" if base < 0.5 else "healthy"),
                processes=processes,
            )
        )

    # System metrics
    if scenario == "healthy":
        cpu = 30 + rng.random() * 40
        mem_used_gb = 45 + rng.random() * 30
        disk = 50 + rng.random() * 20
    elif scenario == "degraded":
        cpu = 60 + rng.random() * 35
        mem_used_gb = 60 + rng.random() * 35
        disk = 70 + rng.random() * 20
    else:
        cpu = 85 + rng.random() * 10
        mem_used_gb = 90 + rng.random() * 30
        disk = 85 + rng.random() * 10

    system_metrics = SystemMetrics(
        cpu_usage_pct=cpu,
        memory_used_gb=mem_used_gb,
        memory_total_gb=128.0,
        disk_usage_pct=disk,
        network_rx_mbps=round(50 + rng.random() * 150, 1),
        network_tx_mbps=round(40 + rng.random() * 120, 1),
        open_file_descriptors=400 + int(rng.random() * 800),
        load_average=[round(cpu / 100 * (1.0 + rng.random()), 2) for _ in range(3)],
    )

    # Health states and events
    health_states: list[HealthState] = []
    events: list[SystemEvent] = []
    now = datetime.now(timezone.utc)

    if scenario == "healthy":
        health_states.append(
            HealthState(component="gpud", health=ComponentHealth.HEALTHY, message="GPUd OK", timestamp=now)
        )
    elif scenario == "degraded":
        health_states.append(
            HealthState(
                component="nvml", health=ComponentHealth.DEGRADED, message="ECC correctable errors detected", timestamp=now
            )
        )
        events.append(
            SystemEvent(timestamp=now, component="driver", level="warning", message="Thermal throttling observed", details={})
        )
        # If any GPU crosses 83°C, explicitly note clock reduction
        if any(g.temperature_c >= 83.0 for g in gpu_metrics):
            events.append(
                SystemEvent(
                    timestamp=now,
                    component="gpu",
                    level="warning",
                    message="Clocks reduced due to thermal cap",
                    details={"threshold_c": 83},
                )
            )
        # Proactive provider response (demo messaging)
        health_states.append(
            HealthState(
                component="provider",
                health=ComponentHealth.HEALTHY,
                message="Hot-swap node pre-warmed; automatic migration available",
                timestamp=now,
            )
        )
        events.append(
            SystemEvent(
                timestamp=now,
                component="provider",
                level="info",
                message="Provider alerted: thermal hotspot detected; replacement node ready",
                details={"action": "hot-swap-standby", "eta": "<30s"},
            )
        )
    else:
        health_states.append(
            HealthState(
                component="gpu", health=ComponentHealth.UNHEALTHY, message="High temperature and XID errors", timestamp=now
            )
        )
        events.append(
            SystemEvent(timestamp=now, component="gpu", level="error", message="Xid error reported", details={"xid": rng.choice([79, 13])})
        )

    machine_info = {
        "gpud_version": "v0.5.1",
        "hostname": (task.name or task.task_id)[:20],
        "gpu_driver": rng.choice(["550.54", "535.129", "470.223"]),
        "cuda_version": rng.choice(["12.4", "12.1", "11.8"]),
        "note": "Demo mode: synthetic metrics",
    }

    snapshot = NodeHealthSnapshot(
        task_id=task.task_id,
        task_name=task.name or task.task_id,
        instance_id=getattr(task, "instance_id", "demo-instance"),
        instance_type=task.instance_type or "demo.gpu",
        timestamp=datetime.now(timezone.utc),
        gpud_healthy=True,
        gpud_version=machine_info.get("gpud_version"),
        machine_info=machine_info,
        gpu_metrics=gpu_metrics,
        system_metrics=system_metrics,
        health_states=health_states,
        events=events,
    )

    # Derived health based on scenario
    if scenario == "healthy":
        snapshot.health_status = HealthStatus.HEALTHY
        snapshot.health_score = 0.9
    elif scenario == "degraded":
        snapshot.health_status = HealthStatus.DEGRADED
        snapshot.health_score = 0.72
    else:
        snapshot.health_status = HealthStatus.CRITICAL
        snapshot.health_score = 0.55

    return snapshot


def summarize_fleet(snapshots: Iterable[NodeHealthSnapshot]) -> FleetHealthSummary:
    """Compute FleetHealthSummary from a collection of snapshots."""
    snaps = list(snapshots)
    monitored = [s for s in snaps if s.health_status != HealthStatus.UNKNOWN]

    total_nodes = len(monitored)
    healthy_nodes = sum(1 for s in monitored if s.health_status == HealthStatus.HEALTHY)
    degraded_nodes = sum(1 for s in monitored if s.health_status == HealthStatus.DEGRADED)
    critical_nodes = sum(1 for s in monitored if s.health_status == HealthStatus.CRITICAL)

    all_gpus = [gpu for s in monitored for gpu in s.gpu_metrics]
    total_gpus = len(all_gpus)
    healthy_gpus = sum(1 for g in all_gpus if g.temperature_c < 75 and not g.is_throttling)

    avg_temp = sum(g.temperature_c for g in all_gpus) / total_gpus if total_gpus else 0.0
    avg_util = (
        sum(g.gpu_utilization_pct for g in all_gpus) / total_gpus if total_gpus else 0.0
    )
    avg_mem = (
        sum(g.memory_utilization_pct for g in all_gpus) / total_gpus if total_gpus else 0.0
    )

    return FleetHealthSummary(
        timestamp=datetime.now(timezone.utc),
        total_nodes=total_nodes,
        healthy_nodes=healthy_nodes,
        degraded_nodes=degraded_nodes,
        critical_nodes=critical_nodes,
        total_gpus=total_gpus,
        healthy_gpus=healthy_gpus,
        avg_gpu_temperature=avg_temp,
        avg_gpu_utilization=avg_util,
        avg_gpu_memory_utilization=avg_mem,
        critical_issues=[],
        warnings=[],
        legacy_nodes=0,
    )


