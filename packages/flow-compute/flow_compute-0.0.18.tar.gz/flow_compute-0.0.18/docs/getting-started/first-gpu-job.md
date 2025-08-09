# Your First GPU Job

Run your first GPU workload with Flow SDK.

## Simplest Example

```python
import flow

# Run a command on GPU
task_id = flow.run("nvidia-smi", instance_type="a100")
print(f"Running on GPU: {task_id}")
```

That's all you need. Flow handles:
- Finding available GPUs
- Setting up the environment
- Running your code
- Returning results

## Complete Example

### 1. Create a Test Script

Save as `gpu_test.py`:

```python
import torch
import time

print("=== GPU Test Started ===")

# Check GPU availability
if torch.cuda.is_available():
    device_name = torch.cuda.get_device_name(0)
    device_count = torch.cuda.device_count()
    memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    
    print(f"GPU Found: {device_name}")
    print(f"Number of GPUs: {device_count}")
    print(f"Memory per GPU: {memory_gb:.1f} GB")
    
    # Run a computation
    print("\nRunning matrix multiplication...")
    size = 10000
    x = torch.randn(size, size).cuda()
    y = torch.randn(size, size).cuda()
    
    start = time.time()
    z = torch.matmul(x, y)
    torch.cuda.synchronize()
    elapsed = time.time() - start
    
    print(f"Computed {size}x{size} matrix multiply in {elapsed:.2f} seconds")
    print(f"FLOPS: {2 * size**3 / elapsed / 1e12:.2f} TFLOPS")
else:
    print("ERROR: No GPU found!")

print("=== GPU Test Complete ===")
```

### 2. Run on Flow

```python
import flow
from flow import TaskConfig

# Configure the job
config = TaskConfig(
    command="python gpu_test.py",
    instance_type="a100",
    max_price_per_hour=10.0  # Safety limit
)

# Submit the job
task_id = flow.run(config)
print(f"Job submitted: {task_id}")

# Monitor the job
from flow import Flow
with Flow() as client:
    task = client.get_task(task_id)
    
    # Wait for completion
    print("Waiting for job to complete...")
    task.wait()
    
    # Get the output
    print("\nJob output:")
    print(task.logs())
```

Expected output:
```
=== GPU Test Started ===
GPU Found: NVIDIA A100-SXM4-80GB
Number of GPUs: 1
Memory per GPU: 79.1 GB

Running matrix multiplication...
Computed 10000x10000 matrix multiply in 0.52 seconds
FLOPS: 3.85 TFLOPS
=== GPU Test Complete ===
```

## Understanding the Flow

### 1. Submit Phase
```python
task_id = flow.run("python script.py", instance_type="a100")
```
- Validates configuration
- Finds available GPU instance
- Submits to cloud provider
- Returns task ID immediately

### 2. Execution Phase
```python
task = client.get_task(task_id)
print(task.status)  # "pending" → "running" → "completed"
```
- Instance provisioned
- Environment set up
- Your code runs
- Output captured

### 3. Results Phase
```python
logs = task.logs()  # Get output
task.wait()         # Block until done
```
- Retrieve logs
- Download results
- Clean up resources

## Common Patterns

### Run with Dependencies

```python
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    image="pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime"
)
task_id = flow.run(config)
```

### Use Multiple GPUs

```python
config = TaskConfig(
    command="torchrun --nproc_per_node=4 train.py",
    instance_type="4xa100"  # 4 A100 GPUs
)
task_id = flow.run(config)
```

### Add Environment Variables

```python
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    env={
        "BATCH_SIZE": "128",
        "LEARNING_RATE": "0.001",
        "WANDB_API_KEY": "your-key"
    }
)
task_id = flow.run(config)
```

### Persistent Storage

```python
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    volumes=[{"name": "training-data", "size_gb": 100}]
)
task_id = flow.run(config)
```

## Monitoring Jobs

### Real-time Logs

```python
from flow import Flow

with Flow() as client:
    task = client.get_task(task_id)
    
    # Stream logs as they arrive
    for line in task.logs(follow=True):
        print(line, end='')
```

### Check Status

```python
status = task.status
# Possible values: "pending", "running", "completed", "failed", "cancelled"

if status == "failed":
    print("Job failed!")
    print(task.logs())  # Check error output
```

### Cost Tracking

```python
# After job completes
print(f"Total runtime: {task.runtime_hours:.2f} hours")
print(f"Total cost: {task.total_cost}")
```

## Command Line Interface

You can also use the CLI:

```bash
# Submit a job
flow run "python train.py" --instance-type a100

# Check all jobs
flow status

# Get logs for specific job
flow logs task-abc123

# Cancel a running job
flow cancel task-abc123
```

## Troubleshooting

### No Instances Available

```python
# Try different instance types
for instance_type in ["a100", "a10g", "v100"]:
    try:
        task_id = flow.run("python script.py", instance_type=instance_type)
        print(f"Success with {instance_type}")
        break
    except Exception as e:
        print(f"{instance_type} not available: {e}")
```

### Task Stays Pending

Common causes:
1. No instances available at your price point
2. Quota limits reached
3. Invalid configuration

Debug with:
```python
# Check available instances
from flow import Flow
with Flow() as client:
    instances = client.find_instances({"gpu_memory_gb": 40})
    for inst in instances:
        print(f"{inst.instance_type}: ${inst.price_per_hour}/hr")
```

### Authentication Issues

Ensure your API key is configured:
```bash
flow init  # Re-run setup
```

Or set directly:
```bash
export Mithril_API_KEY="your-api-key"
```

## Best Practices

1. **Set cost limits**
   ```python
   max_price_per_hour=10.0
   max_run_time_hours=24.0
   ```

2. **Use specific images**
   ```python
   image="pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime"  # Good
   image="pytorch/pytorch:latest"  # Risky - may change
   ```

3. **Name your jobs**
   ```python
   name="experiment-lr-0.001-batch-128"
   ```

4. **Handle failures**
   ```python
   try:
       task_id = flow.run(config)
   except Exception as e:
       print(f"Submission failed: {e}")
       # Try alternative configuration
   ```

## Next Steps

- [Core Concepts](core-concepts.md) - Understand Flow's architecture
- [Authentication](authentication.md) - Configure API access
- [Running Jobs Guide](../guides/running-jobs.md) - Advanced patterns
- [Examples](../../examples/) - Complete working examples