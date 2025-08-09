# Documentation

Welcome to the Flow SDK documentation. Flow provides the simplest way to run code on GPUs.

## Start Here

### [Getting Started Guide](getting-started/)
Everything you need to begin using Flow SDK:
- [Installation](getting-started/installation.md) - Install in 30 seconds
- [Authentication](getting-started/authentication.md) - Configure API access
- [First GPU Job](getting-started/first-gpu-job.md) - Run code on a GPU
- [Core Concepts](getting-started/core-concepts.md) - Understand Flow's design

### [API Reference](API_REFERENCE.md)
Complete reference for all classes and methods:
- Flow class and task submission
- TaskConfig options and validation
- Instance types and selection
- Error handling and recovery

### [User Guide](USER_GUIDE.md)
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
- [Overview](architecture/ARCHITECTURE_OVERVIEW.md) - High-level design
- [Detailed Architecture](architecture/ARCHITECTURE.md) - Component details
- Provider abstraction and security model

## Quick Examples

### Run on GPU
```python
import flow
task_id = flow.run("python train.py", instance_type="a100")
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
task_id = flow.run(config)
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
- [API Status](https://status.mithril.com) - Service availability
- [Support](mailto:support@mithril.com) - Get help

## Requirements

- Python 3.11 or later
- Mithril API key (get from [app.mithril.ai/account/apikeys](https://app.mithril.ai/account/apikeys))

## License

MIT License. See [LICENSE.txt](../LICENSE.txt) for details.