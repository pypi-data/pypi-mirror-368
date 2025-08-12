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
    gpu="h100:8",  # 8x H100 GPUs
    image="pytorch/pytorch:2.0.0",
    volumes={"/data": "training-data"},
    env={"WANDB_API_KEY": "..."}
)
def distributed_training(config_path: str):
    # Multi-GPU training code
    return {"status": "completed"}

# Async execution
task = distributed_training.spawn("config.yaml")
print(task.task_id)
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

## Additional Options

You can further configure behavior via `@app.function(...)` parameters:

- `gpu_memory_gb`: When you don't care about a specific GPU model, select by minimum VRAM.
  ```python
  @app.function(gpu_memory_gb=40)  # any GPU with at least 40GB
  def serve(model_path: str):
      ...
  ```
- `retries`: Retry policy for submission/execution.
  ```python
  from flow.api.models import Retries
  @app.function(retries=Retries.fixed(retries=3, delay=5.0))
  def flaky_job(x: int) -> int:
      return x
  ```
- `max_result_size`: Guard against accidentally huge JSON results (bytes, default 10MB). For large outputs, write to disk and return a path.
  ```python
  @app.function(max_result_size=50*1024*1024)
  def analyze(data_path: str) -> dict:
      ...
  ```