# Pulumi and Flow SDK Integration Guide

## Executive Summary

**Don't build a provider extension. Use Flow SDK directly.**

```python
# Complete integration
import pulumi
import flow

task = flow.run("sleep infinity", instance_type="8xa100", max_price_per_hour=50.0)
pulumi.export("gpu_ips", [i.public_ip for i in task.instances])
```


### Understanding Mithril's Model

Mithril uses spot auctions:
- All instances are preemptible (you can also separately provision reserved/non-preemptible instances via the GUI)
- `max_price_per_hour` is your bid
- Higher bids reduce (don't eliminate) preemption risk

For "persistent" infrastructure:
- Use `sleep infinity` to keep instances running
- Bid high; auctions are second price so you won't pay bid price
- Handle preemption in application layer

## Implementation

### Minimal Wrapper (Optional)

If type safety desired:

```python
# mithril.py (50 lines)
from typing import List
import flow

class Infrastructure:
    """Persistent compute via high spot bids."""
    
    def __init__(self, name: str, gpus: str, bid: float):
        self.task = flow.run(
            "sleep infinity",
            instance_type=gpus,
            max_price_per_hour=bid,
            name=name
        )
        self.task.wait_for_status("RUNNING")
    
    @property
    def ips(self) -> List[str]:
        return [i.public_ip for i in self.task.instances]
    
    def destroy(self):
        self.task.cancel()
```

### Direct Usage (Recommended)

```python
# __main__.py
import pulumi
import flow

# Just use Flow SDK
gpu = flow.run(
    "sleep infinity", 
    instance_type="8xa100",
    max_price_per_hour=50.0
)

pulumi.export("gpu_ip", gpu.instances[0].public_ip)
```

## Patterns

### Bid Strategy

```python
# Constants based on workload criticality
CRITICAL_BID = 100.0 
STANDARD_BID = 50.0 
BATCH_BID = 10.0

# Apply based on use case
training = flow.run(..., max_price_per_hour=CRITICAL_BID)
dev_env = flow.run(..., max_price_per_hour=STANDARD_BID)
batch_job = flow.run(..., max_price_per_hour=BATCH_BID)
```

### Preemption Handling

```python
def create_with_retry(name: str, gpus: str, max_attempts: int = 3):
    """Create infrastructure with preemption retry."""
    
    for attempt in range(max_attempts):
        try:
            task = flow.run(
                "sleep infinity",
                instance_type=gpus,
                max_price_per_hour=50.0,
                name=f"{name}-{attempt}"
            )
            task.wait_for_status("RUNNING", timeout=1200)
            
            # Verify still running after wait
            task.refresh()
            if task.status == "RUNNING":
                return task
                
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            continue
    
    raise Exception("Failed to create stable infrastructure")
```