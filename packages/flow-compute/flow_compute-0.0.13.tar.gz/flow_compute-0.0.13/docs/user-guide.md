# User Guide

## Installation

```bash
pip install flow-sdk
flow init  # Configure API key, project, region
```

## Quick Start

```python
import flow

# Run on GPU
task_id = flow.run("python train.py", instance_type="a100")
print(flow.status(task_id))
```

## Instance Types

```python
"a100"     # 1x A100 80GB
"4xa100"   # 4x A100 80GB
"8xa100"   # 8x A100 80GB
"h100"     # 8x H100 80GB
```

## Task Configuration

### Basic Usage

```python
from flow import TaskConfig

config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    max_price_per_hour=10.0
)
task_id = flow.run(config)
```

### Full Configuration

```python
from flow import TaskConfig, VolumeSpec

config = TaskConfig(
    name="experiment-42",
    command=["python", "train.py", "--config", "large.yaml"],
    instance_type="4xa100",
    
    # Storage
    volumes=[
        VolumeSpec(name="dataset", size_gb=500, mount_path="/data"),
        VolumeSpec(name="checkpoints", size_gb=100, mount_path="/checkpoints")
    ],
    
    # Environment
    env={
        "WANDB_API_KEY": "your-key",
        "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:512"
    },
    
    # Cost controls
    max_price_per_hour=20.0,
    # Optional runtime limit
    # max_run_time_hours=72.0,
    
    # Docker image
    image="nvcr.io/nvidia/pytorch:23.10-py3"
)

task = flow.run(config)
```

## Storage

### Persistent Volumes

```python
# Create and populate
config1 = TaskConfig(
    command="python prepare_data.py",
    volumes=[{"name": "training-data", "size_gb": 100}]
)
task1_id = flow.run(config1)

# Reuse in subsequent tasks
config2 = TaskConfig(
    command="python train.py",
    volumes=[{"name": "training-data"}]
)
task2_id = flow.run(config2)
```

### Dynamic Volume Mounting

Mount volumes to already running tasks without restart:

```python
# Create a volume
volume = flow.create_volume(100, "shared-data")

# Start a long-running task
task = flow.run("python server.py", instance_type="a100")

# Mount volume to the running task
flow.mount_volume("shared-data", task.task_id)
# Volume now available at /mnt/shared-data

# Or use CLI
# flow mount shared-data task_xyz789
# flow mount vol_abc123 gpu-training
# flow mount :1 :2  # Use indices
```

### S3 Integration

```python
task = flow.run(
    """
    aws s3 sync s3://my-bucket/dataset /data/dataset
    python train.py --data /data/dataset
    """,
    volumes=[{"name": "dataset-cache", "size_gb": 100}],
    env={"AWS_ACCESS_KEY_ID": "...", "AWS_SECRET_ACCESS_KEY": "..."}
)
```

## Monitoring

### Logs

```python
from flow import Flow

with Flow() as client:
    task = client.get_task(task_id)
    
    # Stream logs
    for line in task.logs(follow=True):
        print(line)
    
    # Get last 100 lines
    recent_logs = task.logs(tail=100)
```

### Shell Access

```python
task = flow.run(
    "sleep 3600",
    instance_type="a100",
    ssh_keys=["my-key"]
)

# Connect
task.shell()
```

### Task Management

```python
# Status
print(task.status)  # "pending", "running", "completed", "failed"

# Wait
task.wait(timeout=3600)

# Cancel
task.cancel()

# Cost
print(f"Cost: {task.total_cost}")
```

## Distributed Training

```python
# Multi-node setup
task = flow.run(
    "torchrun --nproc_per_node=8 train.py",
    instance_type="8xa100",
    num_instances=4  # 32 GPUs total
)
```

Environment variables:
- `FLOW_NODE_RANK`: Node rank (0-based)
- `FLOW_NUM_NODES`: Total nodes
- `FLOW_MAIN_IP`: Rank 0 IP address

## Common Patterns

### Jupyter Development

```python
config = TaskConfig(
    command="jupyter lab --ip=0.0.0.0 --no-browser",
    instance_type="a100",
    ports=[8888]
)
task = flow.run(config)
print(f"Jupyter URL: http://{task.host}:8888")
```

### Checkpointing

```python
task = flow.run(
    """
    if [ -f /checkpoints/latest.pt ]; then
        python train.py --resume /checkpoints/latest.pt
    else
        python train.py --save-dir /checkpoints
    fi
    """,
    volumes=[{"name": "checkpoints", "mount_path": "/checkpoints"}]
)
```

### Hyperparameter Search

```python
experiments = []
for lr in [0.001, 0.01, 0.1]:
    task = flow.run(
        f"python train.py --lr {lr}",
        instance_type="a100",
        name=f"experiment-lr-{lr}"
    )
    experiments.append(task)

# Monitor results
for task in experiments:
    task.wait()
    print(f"{task.name}: {task.logs(tail=1)}")
```

## Command Formats

```python
# String (shell execution)
flow.run("cd /app && python train.py")

# List (direct execution)
flow.run(["python", "train.py", "--epochs", "100"])

# Script content
script = """
import torch
print(f"GPUs: {torch.cuda.device_count()}")
"""
flow.run(command=script, instance_type="a100")
```

## Cost Management

```python
# Set limits
task = flow.run(
    "python train.py",
    instance_type="a100",
    max_price_per_hour=10.0,      # Use spot when available
    # max_run_time_hours=24.0       # Optional: force stop after 24h
)

# Monitor costs
with Flow() as client:
    tasks = client.list_tasks(limit=10)
for t in tasks:
    print(f"{t.task_id}: {t.total_cost}")
```

## Troubleshooting

### Debug Mode

```python
import os
os.environ["FLOW_DEBUG"] = "1"
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Task pending | Check `flow.find_instances({})`, verify quota |
| No instances | Increase `max_price_per_hour`, try different type |
| Shell refused | Add `ssh_keys`, wait for "running" state |
| OOM errors | Use larger GPU, reduce batch size |

## Best Practices

1. **Set cost limits**: `max_price_per_hour` (and optionally `max_run_time_hours`)
2. **Use specific types**: `"4xa100"` not `min_gpu_count=4`
3. **Name descriptively**: `name="bert-finetune-squad-v2"`
4. **Persist checkpoints**: Use volumes for training state
5. **Monitor actively**: Stream logs during execution
6. **Clean up**: Remember to terminate instances when done