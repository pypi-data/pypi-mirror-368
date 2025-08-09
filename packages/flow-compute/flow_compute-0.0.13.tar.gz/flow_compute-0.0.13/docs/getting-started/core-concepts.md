# Core Concepts

Understanding Flow SDK's core concepts helps you use it effectively.

## Tasks

A **task** is your code running on GPU infrastructure. When you submit a task, Flow handles:
- Finding available GPUs
- Setting up the environment
- Running your code
- Capturing output
- Cleaning up resources

### Task Lifecycle

```
Pending → Provisioning → Running → Completed
                ↓            ↓
             Failed      Cancelled
```

**States:**
- `pending`: Waiting for available GPU
- `provisioning`: Setting up instance
- `running`: Your code is executing
- `completed`: Finished successfully
- `failed`: Error occurred
- `cancelled`: Manually stopped

### Task Configuration

Configure tasks with `TaskConfig`:

```python
from flow import TaskConfig

config = TaskConfig(
    name="experiment-42",
    command="python train.py",
    instance_type="a100",
    volumes=[{"name": "data", "size_gb": 100}],
    env={"WANDB_PROJECT": "ml-research"},
    max_price_per_hour=10.0,
    # Optional: set a time limit to auto-terminate
    # max_run_time_hours=24.0
)
```

### Task Objects

When you submit a task with `flow.run()`, it returns a `Task` object that provides full control and monitoring:

```python
# Submit task
task = flow.run(config)

# Access task information
print(f"Task ID: {task.task_id}")
print(f"Status: {task.status}")
print(f"Cost per hour: {task.cost_per_hour}")

# Monitor execution
task.wait()  # Block until complete
print(task.logs())  # Get output

# Shell access (requires SSH key)
if task.is_running:
    task.shell()  # Interactive session
    task.shell(command="nvidia-smi")  # Run command
```

Key Task attributes:
- `task_id`: Unique identifier
- `status`: Current state (TaskStatus enum)
- `cost_per_hour`: Hourly cost (e.g., "$25.60")
- `shell_command`: Shell connection string
- `endpoints`: Service URLs (e.g., Jupyter)

Key Task methods:
- `logs()`: Get output logs
- `wait()`: Block until completion
- `stop()`: Cancel execution
- `shell()`: Shell into instance
- `refresh()`: Update task info

## Instance Types

Instance types define the GPU hardware for your task.

### Naming Convention

Flow uses simple, memorable names:

```python
"a100"     # 1x A100 80GB
"4xa100"   # 4x A100 80GB
"8xa100"   # 8x A100 80GB
"h100"     # 8x H100 80GB (default configuration)
```

### Full Specification

For precise control:

```python
"a100-80gb.sxm.1x"      # A100 80GB SXM interconnect
"h100-80gb.pcie.1x"     # H100 80GB PCIe variant
```

### Capability-Based Selection

Let Flow find the best option:

```python
config = TaskConfig(
    command="python train.py",
    min_gpu_memory_gb=40  # Any GPU with 40GB+ VRAM
)
```

## Volumes

Volumes provide persistent storage across tasks.

### How Volumes Work

1. **Created on first use**: Automatically provisioned
2. **Persist between tasks**: Data remains after task completes
3. **Shared across tasks**: Multiple tasks can access same volume
4. **Project-scoped**: Accessible within your project

### Using Volumes

```python
# First task: prepare data
config1 = TaskConfig(
    command="python prepare_data.py",
    volumes=[{"name": "dataset", "size_gb": 500}]
)

# Later task: use prepared data
config2 = TaskConfig(
    command="python train.py",
    volumes=[{"name": "dataset"}]  # Reuses existing volume
)
```

### Mount Paths

Volumes mount at `/volumes/<name>` by default:

```python
volumes=[{"name": "data", "mount_path": "/data"}]
# Your code accesses files at /data/
```

## Environment Configuration

### Docker Images

Tasks run in Docker containers:

```python
# Default image
image="ubuntu:22.04"

# Deep learning frameworks
image="pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime"
image="tensorflow/tensorflow:latest-gpu"

# Custom images
image="your-registry.com/custom-ml:v1.0"
```

### Environment Variables

Pass configuration without modifying code:

```python
env={
    "BATCH_SIZE": "128",
    "LEARNING_RATE": "0.001",
    "WANDB_API_KEY": "your-key",
    "CUDA_VISIBLE_DEVICES": "0,1"  # Use specific GPUs
}
```

## Cost Management

### Price Limits

Prevent unexpected costs:

```python
max_price_per_hour=10.0  # Use spot instances when possible
```

### Time Limits (optional)

Automatic termination can be configured if desired:

```python
max_run_time_hours=24.0  # Optional, stop after 24 hours
```

### Task Lifecycle

Tasks run until completion or until stopped manually. You can optionally set runtime limits when you want auto-termination.

## Multi-Node Training

For distributed workloads:

```python
config = TaskConfig(
    command="torchrun train_distributed.py",
    instance_type="8xa100",
    num_instances=4  # 4 nodes × 8 GPUs = 32 total
)
```

Flow sets environment variables:
- `FLOW_NODE_RANK`: Node index (0, 1, 2, 3)
- `FLOW_NUM_NODES`: Total nodes (4)
- `FLOW_MAIN_IP`: IP of rank 0 node

## Shell Access

Debug running tasks:

```python
# Get task object
from flow import Flow
with Flow() as client:
    task = client.get_task(task_id)
    
    # Shell into instance
    task.shell()
    
    # Or get shell command
    print(task.shell_command)
    # Output: ssh -i ~/.ssh/key ubuntu@1.2.3.4
```

## Provider Architecture

Flow SDK uses a provider pattern:

```
Your Code
    ↓
Flow SDK (provider-agnostic API)
    ↓
Provider Implementation (Mithril)
    ↓
Cloud Infrastructure
```

Currently supports:
- **Mithril**  - Production ready
- **Local** - Development/testing

Future providers:
- AWS
- GCP
- Azure

## Error Handling

Flow provides clear, actionable errors:

```python
from flow.errors import (
    ValidationError,          # Invalid configuration
    ResourceNotFoundError,    # Instance type unavailable
    InsufficientQuotaError,   # Quota exceeded
    AuthenticationError       # API key issues
)

try:
    task_id = flow.run("train.py", instance_type="a100")
except ResourceNotFoundError as e:
    print(f"No A100s available: {e}")
    # Try alternative
    task_id = flow.run("train.py", instance_type="v100")
```

## Configuration Hierarchy

Settings are resolved in order:

1. **Direct arguments** (highest priority)
   ```python
   flow.run("script.py", instance_type="a100")
   ```

2. **Environment variables**
   ```bash
   export Mithril_REGION="us-west1-a"
   ```

3. **Config file** (`~/.flow/config.yaml`)
   ```yaml
   region: us-central1-a
   ```

4. **Defaults** (lowest priority)

## Best Practices

### 1. Set Resource Limits
```python
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    max_price_per_hour=10.0,
    # Optional time limit
    # max_run_time_hours=24.0
)
```

### 2. Use Volumes for Data
```python
# Good: Data persists
volumes=[{"name": "dataset", "size_gb": 100}]

# Bad: Re-downloads every time
command="wget https://example.com/data.tar && python train.py"
```

### 3. Name Tasks Descriptively
```python
name="bert-finetune-lr0.001-batch32"
```

### 4. Handle Failures Gracefully
```python
for gpu in ["a100", "v100", "a10g"]:
    try:
        task_id = flow.run("train.py", instance_type=gpu)
        break
    except Exception as e:
        print(f"{gpu} failed: {e}")
```

## Next Steps

- [Running Jobs Guide](../guides/running-jobs.md) - Advanced patterns
- [API Reference](../API_REFERENCE.md) - Complete reference
- [Examples](../../examples/) - Working code samples