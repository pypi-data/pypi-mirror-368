# Decorator Pattern

Flow SDK provides a decorator-based API similar to popular serverless frameworks:

## Basic Usage

```python
from flow import FlowApp

app = FlowApp()

@app.function(gpu="a100")
def train_model(data_path: str, epochs: int = 100):
    import torch
    model = torch.nn.Linear(10, 1)
    # ... training logic ...
    return {"accuracy": 0.95, "loss": 0.01}

# Execute remotely on GPU
result = train_model.remote("s3://data.csv", epochs=50)

# Execute locally for testing
local_result = train_model("./local_data.csv")
```

## Advanced Configuration

```python
@app.function(
    gpu="8xh100",  # 8x H100 GPUs
    image="pytorch/pytorch:2.0.0",
    volumes={"/data": "training-data"},
    env={"WANDB_API_KEY": "..."}
)
def distributed_training(config_path: str):
    # Multi-GPU training code
    return {"status": "completed"}

# Async execution
task_id = distributed_training.spawn("config.yaml")
```

## Module-Level Usage

```python
from flow import function

# Use without creating an app instance
@function(gpu="a100")
def inference(text: str) -> dict:
    # Run inference
    return {"sentiment": "positive"}
```

The decorator pattern provides:
- **Clean syntax**: Familiar to Flask/FastAPI users
- **Local testing**: Call functions directly without infrastructure
- **Type safety**: Full IDE support and type hints
- **Flexibility**: Mix local and remote execution seamlessly