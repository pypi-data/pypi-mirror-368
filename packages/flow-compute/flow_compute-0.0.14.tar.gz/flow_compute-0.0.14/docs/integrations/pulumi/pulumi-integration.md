# Pulumi and Flow SDK Integration Recommendation

Use Flow SDK directly in Pulumi programs. No provider needed.

## Quick Start

```python
import pulumi
import flow

# Infrastructure
task = flow.run(
    "sleep infinity",
    instance_type="8xa100",
    max_price_per_hour=50.0,  # High bid prevents preemption
    name="gpu-infra"
)

# Export state
pulumi.export("task_id", task.task_id)
pulumi.export("ips", [i.public_ip for i in task.instances])
```

## Core Concepts

### Spot Bidding

Mithril allocates compute via spot auctions. Your `max_price_per_hour` is your bid.

**Infrastructure** (persistent):
- Bid ≥ on-demand price ($25+ for A100, $50+ for H100)
- Higher bids reduce preemption risk

**Workloads** (ephemeral):
- Lower bids acceptable
- Design for interruption

### Task Model

Flow SDK tasks represent compute jobs, not infrastructure. For persistent compute:

1. Use `"sleep infinity"` to keep instances alive
2. Set high `max_price_per_hour` to avoid preemption
3. Handle preemption gracefully

## Patterns

### GPU Infrastructure

```python
def create_gpu_cluster(name: str, gpus: str = "8xa100") -> dict:
    """Create persistent GPU infrastructure."""
    
    # High bid for stability
    bid = 50.0 if "h100" in gpus else 25.0
    
    task = flow.run(
        "sleep infinity",
        instance_type=gpus,
        max_price_per_hour=bid,
        name=name
    )
    
    task.wait_for_status("RUNNING")
    
    return {
        "id": task.task_id,
        "ips": [i.public_ip for i in task.instances]
    }
```

### Workload Execution

```python
def run_training(script: str, data_volume: str) -> str:
    """Run ML training job."""
    
    task = flow.run(
        f"python {script}",
        instance_type="4xa100",
        volumes=[{"volume_id": data_volume, "mount_path": "/data"}],
        max_price_per_hour=15.0  # Lower bid OK for batch jobs
    )
    
    return task.task_id
```

### Complete Example

```python
# infrastructure.py
import pulumi
import flow

# Storage
from flow import Flow
with Flow() as client:
    data = client.create_volume(1000, "training-data")
    models = client.create_volume(500, "models")

# Compute
cluster = flow.run(
    "sleep infinity",
    instance_type="8xa100",
    num_instances=4,
    max_price_per_hour=50.0,
    volumes=[
        {"volume_id": data.volume_id, "mount_path": "/data"},
        {"volume_id": models.volume_id, "mount_path": "/models"}
    ]
)

# Exports
pulumi.export("cluster_id", cluster.task_id)
pulumi.export("gpu_ips", [i.public_ip for i in cluster.instances])
pulumi.export("storage", {
    "data": data.volume_id,
    "models": models.volume_id
})
```

## Testing

```python
# Mock for tests
if os.getenv("TEST"):
    flow.run = lambda *a, **k: type('Task', (), {
        'task_id': 'test-123',
        'instances': [type('', (), {'public_ip': '10.0.0.1'})()],
        'wait_for_status': lambda *a: None
    })()
```