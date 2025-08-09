# Running Jobs

This guide covers advanced patterns and best practices for running GPU workloads with Flow SDK.

## Overview

Flow SDK provides multiple ways to submit jobs, from simple one-liners to complex multi-node configurations.

## Basic Job Submission

### The Simplest Way

```python
import flow

# Run on any available GPU
task_id = flow.run("python train.py")

# Specify GPU type
task_id = flow.run("python train.py", instance_type="a100")
```

### Using Task Configuration

```python
from flow import TaskConfig

# Basic configuration
config = TaskConfig(
    command="python train.py",
    instance_type="a100"
)
task_id = flow.run(config)

# With environment variables
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    env={
        "EPOCHS": "100",
        "BATCH_SIZE": "64",
        "LEARNING_RATE": "0.001"
    }
)
task_id = flow.run(config)
```

## Complete Task Configuration

The `TaskConfig` model provides full control over job execution:

```python
from flow import TaskConfig

config = TaskConfig(
    # Basic settings
    name="bert-training",
    command="python train.py --model bert-base",
    
    # Instance selection (use one approach)
    instance_type="a100",  # Simple name
    # OR
    min_gpu_memory_gb=80,  # Capability-based
    
    # Environment
    image="pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime",
    env={
        "WANDB_PROJECT": "bert-experiments",
        "BATCH_SIZE": "32"
    },
    
    # Storage
    volumes=[
        {"name": "data", "mount_path": "/data"},
        {"name": "cache", "mount_path": "/cache"}
    ],
    
    # Cost control (optional)  
    # max_run_time_hours=24.0,  # Optional auto-terminate after 24h
    max_price_per_hour=10.0,    # Cost limit
    
    # SSH access
    ssh_keys=["my-key"],  # SSH key names
    
    # Advanced
    region="us-central1-a",  # Specific region
    num_instances=1          # Single node (can be multiple)
)

task_id = flow.run(config)
```

## Instance Selection

### Simple Names (Recommended)

```python
# Simple instance names
task_id = flow.run("python script.py", instance_type="a100")
task_id = flow.run("python script.py", instance_type="4xa100")
task_id = flow.run("python script.py", instance_type="8xh100")

# Common patterns:
# - "a100"     # 1x A100 80GB
# - "2xa100"   # 2x A100 80GB
# - "4xa100"   # 4x A100 80GB  
# - "8xa100"   # 8x A100 80GB
# - "h100"     # 8x H100 80GB (default)
# - "8xh100"   # 8x H100 80GB (explicit)
```

### Full Specification

```python
# Mithril canonical format
task_id = flow.run("python script.py", instance_type="a100-80gb.sxm.1x")
task_id = flow.run("python script.py", instance_type="h100-80gb.pcie.1x")
```

### Capability-Based Selection

```python
# Let Flow find the cheapest option
config = TaskConfig(
    command="python train_large_model.py",
    min_gpu_memory_gb=80,     # At least 80GB VRAM
    max_price_per_hour=10.0   # Budget constraint
)
task_id = flow.run(config)
```

## Working with Docker Images

### Default Image

```python
# Uses Ubuntu 22.04 by default
task_id = flow.run("python train.py")

# Explicit default
config = TaskConfig(
    command="python train.py",
    image="ubuntu:22.04"
)
task_id = flow.run(config)
```

### Framework Images

```python
# PyTorch
config = TaskConfig(
    command="python train.py",
    image="pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime"
)
task_id = flow.run(config)

# TensorFlow
config = TaskConfig(
    command="python train.py",
    image="tensorflow/tensorflow:2.14.0-gpu"
)
task_id = flow.run(config)

# NVIDIA NGC
config = TaskConfig(
    command="python train.py",
    image="nvcr.io/nvidia/pytorch:23.10-py3"
)
task_id = flow.run(config)
```

## Environment Setup

### Environment Variables

```python
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    env={
        # Training parameters
        "EPOCHS": "100",
        "BATCH_SIZE": "32",
        
        # External services
        "WANDB_API_KEY": "your-wandb-key",
        "HF_TOKEN": "your-huggingface-token",
        
        # CUDA settings
        "CUDA_VISIBLE_DEVICES": "0,1",
        "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:512"
    }
)
task_id = flow.run(config)
```

### Setup Commands

```python
# Run setup commands before your main script
config = TaskConfig(
    command="pip install -r requirements.txt && python train.py",
    instance_type="a100"
)
task_id = flow.run(config)

# Or use multiple commands
config = TaskConfig(
    command=[
        "apt-get update && apt-get install -y libgl1",
        "pip install -r requirements.txt",
        "python train.py"
    ],
    instance_type="a100"
)
task_id = flow.run(config)
```

## Monitoring and Control

### Checking Status

```python
from flow import Flow

# Submit job
task_id = flow.run("python long_training.py", instance_type="a100")

# Get task status
with Flow() as client:
    task = client.get_task(task_id)
    print(f"Status: {task.status()}")  # "pending", "running", "completed", etc.
    
    # Wait for completion
    task.wait()
    print("Job completed!")
```

### Viewing Logs

```python
# Get logs after completion
logs = task.logs()
print(logs)

# Stream logs in real-time
for line in task.logs(follow=True):
    print(line, end='')
```

### Shell Access

```python
# Shell into running instance
task.shell()

# Get shell command
shell_cmd = task.shell_command
print(shell_cmd)  # ssh -i ~/.ssh/key ubuntu@1.2.3.4
```

## Handling Long-Running Jobs

### Auto-termination (optional)

```python
# Set maximum runtime
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    max_run_time_hours=48.0  # Optional: auto-stop after 2 days
)
task_id = flow.run(config)
```

### Checkpointing with Volumes

```python
# Use persistent volumes for checkpoints
config = TaskConfig(
    command="python train.py --checkpoint-dir /checkpoints",
    instance_type="a100",
    volumes=[{"name": "checkpoints", "mount_path": "/checkpoints"}],
    env={"CHECKPOINT_FREQUENCY": "1000"}  # Save every 1000 steps
)
task_id = flow.run(config)

# Resume from checkpoint in next run
config = TaskConfig(
    command="python train.py --resume /checkpoints/latest.pt",
    instance_type="a100",
    volumes=[{"name": "checkpoints", "mount_path": "/checkpoints"}]
)
task_id = flow.run(config)
```

## Cost Management

### Price Limits

```python
# Set maximum hourly cost
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    max_price_per_hour=5.0  # Use spot instances when available
)
task_id = flow.run(config)

# Capability-based with price limit
config = TaskConfig(
    command="python train.py",
    min_gpu_memory_gb=80,
    max_price_per_hour=5.0  # Find cheapest 80GB+ GPU under $5/hr
)
task_id = flow.run(config)
```

### Runtime Limits (optional)

```python
# Set runtime limit
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    max_run_time_hours=24.0  # Optional: hard stop after 24 hours
)
task_id = flow.run(config)
```

## Multi-Node Jobs

### Basic Multi-Node

```python
# Launch 4 nodes with 1 GPU each
config = TaskConfig(
    command="python distributed_train.py",
    instance_type="a100",
    num_instances=4
)
task_id = flow.run(config)
```

### Distributed PyTorch Training

```python
# 4 nodes × 8 GPUs = 32 GPUs total
config = TaskConfig(
    command="torchrun --nproc_per_node=8 train.py",
    instance_type="8xa100",
    num_instances=4,
    env={
        "MASTER_PORT": "29500"
    }
)
task_id = flow.run(config)

# You must manually set environment variables for node coordination
```

### Multi-Node Configuration

```python
# For multi-node training, set coordination variables explicitly
config = TaskConfig(
    command="torchrun --nproc_per_node=8 train.py",
    instance_type="8xa100",
    num_instances=4,
    env={
        "FLOW_NODE_RANK": "0",  # Set differently for each node
        "FLOW_NUM_NODES": "4",
        "FLOW_MAIN_IP": "10.0.0.1",  # IP of rank 0 node
        "MASTER_PORT": "29500"
    }
)
```

## Error Handling

### Catching Exceptions

```python
from flow.errors import (
    ResourceNotFoundError,
    InsufficientQuotaError,
    ValidationError
)

try:
    task_id = flow.run("python train.py", instance_type="a100")
except ResourceNotFoundError as e:
    print(f"No A100s available: {e}")
    # Try alternative GPU
    task_id = flow.run("python train.py", instance_type="v100")
except InsufficientQuotaError as e:
    print(f"Quota exceeded: {e}")
    # Try smaller instance
    task_id = flow.run("python train.py", instance_type="a10g")
except ValidationError as e:
    print(f"Configuration error: {e}")
    # Fix configuration and retry
```

### Automatic Fallback

```python
# Try GPUs in order of preference
gpu_preferences = ["a100", "a10g", "v100", "t4"]

for gpu in gpu_preferences:
    try:
        task_id = flow.run("python train.py", instance_type=gpu)
        print(f"Successfully launched on {gpu}")
        break
    except Exception as e:
        print(f"{gpu} not available: {e}")
        if gpu == gpu_preferences[-1]:
            raise  # Re-raise if no GPUs available
```

## Best Practices

### 1. Use Descriptive Names

```python
# Good - descriptive and searchable
config = TaskConfig(
    name="bert-base-imdb-lr0.001-batch32",
    command="python train.py",
    instance_type="a100"
)

# Bad - generic name
config = TaskConfig(
    name="test",
    command="python train.py",
    instance_type="a100"
)
```

### 2. Version Your Images

```python
# Good - reproducible
image="pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime"

# Bad - might change
image="pytorch/pytorch:latest"
```

### 3. Use Volumes for Persistence

```python
# Save checkpoints and results
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    volumes=[
        {"name": "checkpoints", "mount_path": "/checkpoints"},
        {"name": "results", "mount_path": "/results"}
    ],
    env={
        "CHECKPOINT_DIR": "/checkpoints",
        "OUTPUT_DIR": "/results"
    }
)
```

### 4. Set Limits Thoughtfully

```python
# Prevent runaway costs
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    # Optional
    # max_run_time_hours=24.0,
    max_price_per_hour=10.0
)
```

### 5. Handle Interruptions

```python
# Save progress regularly
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    volumes=[{"name": "checkpoints"}],
    env={
        "SAVE_STEPS": "500",
        "RESUME": "auto"
    }
)
```

## Command-Line Interface

```bash
# Submit jobs from CLI
flow run "python train.py" --instance-type a100

# With options
flow run "python train.py" \
  --instance-type a100 \
  --max-price 10 \
  --max-hours 24 \
  --volume checkpoints:100:/checkpoints

# Check status
flow status

# View logs
flow logs task-abc123

# Cancel job
flow cancel task-abc123
```

## Next Steps

- [Data Management](data-management.md) - Working with volumes and datasets
- [Advanced Patterns](../advanced/patterns.md) - Complex workflows
- [Monitoring](monitoring.md) - Debugging and optimization
- [API Reference](../API_REFERENCE.md) - Complete API documentation