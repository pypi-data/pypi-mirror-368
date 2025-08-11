# xAI Pulumi and Flow SDK Recommendation

## TL;DR

Use Flow SDK directly in your Pulumi programs. No provider needed.

```python
# infrastructure/__main__.py
import pulumi
import flow

gpu = flow.run("sleep infinity", instance_type="8xa100", max_price_per_hour=50.0)
pulumi.export("gpu_ip", gpu.instances[0].public_ip)
```

## Architecture

```
Your Pulumi Program (Python)
    ↓ imports
Flow SDK (Python library)
    ↓ API calls
Mithril Infrastructure (spot GPUs)
```

## Why This Works

1. **Zero abstraction overhead** - Direct API usage
2. **Available today** - No development needed
3. **Full control** - All Flow SDK features accessible
4. **Clear mental model** - No leaky abstractions

## Key Insight: Spot Instances

Mithril GPUs are spot instances with bidding:
- Your `max_price_per_hour` is your bid
- Higher bids reduce preemption risk
- Infrastructure needs high bids ($50+ for A100s)
- Workloads can use lower bids

## Production Pattern

```python
# production.py
import pulumi
import flow

# High bids for stability
INFRA_BIDS = {
    "a100": 25.0,
    "8xa100": 50.0,
    "h100": 100.0
}

# Storage (persistent)
from flow import Flow
with Flow() as client:
    data = client.create_volume(2000, "prod-data")
    models = client.create_volume(500, "prod-models")

# Compute (preemptible)
cluster = flow.run(
    "sleep infinity",
    instance_type="8xa100",
    num_instances=8,
    max_price_per_hour=INFRA_BIDS["8xa100"],
    volumes=[
        {"volume_id": data.volume_id, "mount_path": "/data"},
        {"volume_id": models.volume_id, "mount_path": "/models"}
    ]
)

# Export for other stacks
pulumi.export("cluster", {
    "id": cluster.task_id,
    "ips": [i.public_ip for i in cluster.instances]
})
```

## Preemption Handling

Design for failure:

```python
def create_resilient_cluster(name: str, size: int):
    """Create cluster with preemption handling."""
    
    tasks = []
    for i in range(size):
        task = flow.run(
            "sleep infinity",
            instance_type="a100",
            max_price_per_hour=30.0,
            name=f"{name}-{i}"
        )
        tasks.append(task)
    
    # Monitor and replace preempted instances
    # (Implement based on your requirements)
    
    return tasks
```

## Testing

```python
# Override for tests
if os.getenv("DRY_RUN"):
    flow.run = lambda *a, **k: MockTask()
```

## Next Steps

1. Try the [examples](examples/)
2. Set appropriate bid prices for your workloads
3. Implement preemption monitoring
4. No provider development needed

## Questions?

The simplest solution is the best solution.