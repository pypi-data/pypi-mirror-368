# Documentation

Welcome to the Flow documentation. Flow provides the simplest way to run code on GPUs.

## Start Here

### [Getting Started Guide](getting-started/)
Everything you need to begin using Flow:
- [Installation](getting-started/installation.md) - Install in 30 seconds
- [Authentication](getting-started/authentication.md) - Configure API access
- [First GPU Job](getting-started/first-gpu-job.md) - Run code on a GPU
- [Core Concepts](getting-started/core-concepts.md) - Understand Flow's design

### [API Reference](api-reference.md)
Complete reference for all classes and methods:
- Flow class and task submission
- TaskConfig options and validation
- Instance types and selection
- Error handling and recovery

### [User Guide](user-guide.md)
Practical patterns and workflows:
- Training models with checkpointing
- Running Jupyter notebooks on GPUs
- Distributed multi-node training
- Cost management strategies

### [Decorator Pattern](guides/decorator-pattern.md)
Function-based GPU execution with decorators:
- Clean pythonic API similar to serverless frameworks
- Remote and local execution with the same code
- Advanced resource configuration
- Integration with other Flow patterns

### [Architecture](architecture/)
Technical deep dive into Flow's design:
- [Overview](architecture/architecture-overview.md) - High-level design
- [Detailed Architecture](architecture/architecture.md) - Component details
- Provider abstraction and security model

### [CLI Reference](cli/command-reference.md)
Quick list of available `flow` commands

## Quick Examples

### Run on GPU
```python
import flow
task = flow.run("python train.py", instance_type="a100")
```

### Decorator Pattern
```python
from flow import FlowApp

app = FlowApp()

@app.function(gpu="a100")
def train_model(data_path: str):
    import torch
    # Training logic
    return {"loss": 0.01}

# Remote execution
result = train_model.remote("s3://bucket/data.csv")

# Async execution
task = train_model.spawn("s3://bucket/data.csv")
print(task.task_id)
```

### With Configuration
```python
from flow import TaskConfig
config = TaskConfig(
    command="python train.py",
    instance_type="4xa100",
    volumes=[{"name": "data", "size_gb": 100}],
    max_price_per_hour=10.0
)
task = flow.run(config)
```

### Monitor Progress
```python
from flow import Flow
with Flow() as client:
    task = client.get_task(task_id)
    for line in task.logs(follow=True):
        print(line)
```

## Resources

- [Examples](../examples/) - Complete working examples
- [API Status][status] - Service availability
- [Support](mailto:support@mithril.ai) - Get help
- [Instance quotas][quotas_instances] and [Storage quotas][quotas_storage]

## Requirements

- Python 3.10 or later
- Mithril API key (get from [app.mithril.ai/account/apikeys][api_keys])

[status]: {{ STATUS_BASE }}
[api_keys]: {{ WEB_BASE }}/account/apikeys
[quotas_instances]: {{ WEB_BASE }}/instances/quotas
[quotas_storage]: {{ WEB_BASE }}/storage/quotas

## License

Apache 2.0 License. See [LICENSE.txt](../LICENSE.txt) for details.