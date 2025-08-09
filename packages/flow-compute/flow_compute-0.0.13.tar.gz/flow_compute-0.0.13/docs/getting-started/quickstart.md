# Quickstart

Run your first GPU job in under 5 minutes.

> **📚 Looking for more detailed guides?** Check out our [comprehensive quickstart documentation](../quickstart/index.md) with paths for SDK users, CLI users, and platform teams.

## 1. Install

```bash
pip install flow-sdk
```

## 2. Configure

```bash
uv run flow init
```

This will prompt for your Mithril API key. Get one at [app.mithril.ai/account/apikeys](https://app.mithril.ai/account/apikeys).

## 3. Run on GPU

```python
import flow

# Submit a simple command
task_id = flow.run("nvidia-smi", instance_type="a100")
print(f"Task submitted: {task_id}")
```

That's it! Your code is running on an A100 GPU.

## Full Example

### Create a GPU test script

Save as `gpu_test.py`:

```python
import torch

# Check GPU availability
if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"GPU: {gpu_name}")
    print(f"Memory: {gpu_memory:.1f} GB")
    
    # Run a simple computation
    x = torch.randn(5000, 5000).cuda()
    y = torch.randn(5000, 5000).cuda()
    z = torch.matmul(x, y)
    print(f"Computed {z.shape} matrix on GPU")
else:
    print("No GPU found!")
```

### Run it on Flow

```python
import flow
from flow import TaskConfig

# Configure the task
config = TaskConfig(
    command="python gpu_test.py",
    instance_type="a100",
    max_price_per_hour=10.0  # Cost protection
)

# Submit and monitor
task = flow.run(config)
print(f"Running on GPU: {task.task_id}")

# Wait and print logs
task.wait()
print(task.logs())
```

## Common Patterns

### Training with Volumes

```python
from flow import TaskConfig

config = TaskConfig(
    command="python train.py",
    instance_type="4xa100",  # 4 GPUs
    volumes=[{"name": "dataset", "size_gb": 100}],
    max_run_time_hours=24.0
)
task_id = flow.run(config)
```

### Jupyter Notebook

```python
from flow import TaskConfig

config = TaskConfig(
    command="jupyter lab --ip=0.0.0.0",
    instance_type="a100",
    ports=[8888]
)
task_id = flow.run(config)
```

### With Environment Variables

```python
from flow import TaskConfig

config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    env={
        "WANDB_API_KEY": "your-key",
        "EXPERIMENT_NAME": "baseline"
    }
)
task_id = flow.run(config)
```

## Command Line Interface

```bash
# Submit a job
uv run flow run "python train.py" --instance-type a100

# Check status
uv run flow status

# View logs
uv run flow logs task-abc123

# Cancel a job
uv run flow cancel task-abc123
```

## Instance Types

Common GPU types (Mithril):

```python
"a100"     # 1x A100 80GB
"2xa100"   # 2x A100 80GB
"4xa100"   # 4x A100 80GB
"8xa100"   # 8x A100 80GB
"h100"     # 8x H100 80GB
```

> **Note:** Mithril uses dynamic auction-based pricing. Check current rates with `flow instances`.

## Cost Control

Always set limits:

```python
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    max_price_per_hour=10.0,      # Don't exceed $10/hr
    max_run_time_hours=24.0       # Stop after 24 hours
)
```

## Troubleshooting

### No instances available

Try:
- Different instance type: `"a100"` → `"a10g"`
- Higher price limit: `max_price_per_hour=15.0`
- Different region in config

### Task stays pending

Check:
- Instance availability: `flow.find_instances({})`
- Your quota limits
- API key permissions

### Import errors

Ensure:
- Python 3.11+: `python --version`
- Flow installed: `pip show flow-sdk`
- Correct import: `import flow` (not `from flow import Flow`)

## Next Steps

### Quick Links
- **[Comprehensive Quickstart Hub](../quickstart/index.md)** - Choose your path:
  - [SDK Quickstarts](../quickstart/sdk/inference.md) - Python API examples
  - [CLI Quickstarts](../quickstart/cli/inference.md) - Command-line workflows
  - [IaC Quickstarts](../quickstart/iac/terraform.md) - Infrastructure as Code
  - [Interactive Notebooks](../quickstart/notebook/getting-started.ipynb) - Jupyter tutorials

### Core Documentation
- [Authentication Guide](authentication.md) - Configure API access
- [Core Concepts](core-concepts.md) - Understand Flow's design
- [Running Jobs](../guides/running-jobs.md) - Advanced patterns
- [Examples](../../examples/) - Complete working examples