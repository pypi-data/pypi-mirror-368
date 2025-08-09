# Invoker Pattern

Execute Python functions on remote GPUs without contaminating user code with infrastructure dependencies.

## Design

User code remains pure Python:

```python
# train.py
def train_model(data_path: str, epochs: int = 100):
    import torch
    model = torch.nn.Linear(10, 1)
    # ML logic
    return {"accuracy": 0.95, "loss": 0.01}
```

Infrastructure stays separate:

```python
# runner.py
from flow import invoke

result = invoke("train.py", "train_model", 
                args=["s3://bucket/data"],
                kwargs={"epochs": 200},
                gpu="a100")
```

## API

```python
def invoke(
    module_path: str,
    function_name: str,
    args: Optional[List[Any]] = None,
    kwargs: Optional[dict[str, Any]] = None,
    **task_params
) -> Any:
    """Execute function remotely. Args/kwargs must be JSON-serializable."""

def invoke_async(...) -> InvokeTask:
    """Non-blocking variant. Returns handle for monitoring."""
```

Task parameters: `gpu`, `instance_type`, `max_price_per_hour`, `max_run_time_hours`, `volumes`, `env`.

## Constraints

1. Arguments and returns must be JSON-serializable (10MB limit)
2. Pass data via paths, not values
3. Remote modules must be available in execution environment
4. No streaming - results returned on completion

## Examples

### Basic

```python
# Local or remote execution
pi = invoke("math_ops.py", "calculate_pi", args=[1000000])
```

### GPU Training

```python
metrics = invoke(
    "model_training.py",
    "train_bert",
    args=["s3://datasets/imdb"],
    kwargs={"config": {"batch_size": 32, "epochs": 3}},
    gpu="a100",
    max_price_per_hour=10.0
)
```

### Parallel Experiments

```python
tasks = []
for seed in range(10):
    for lr in [0.001, 0.01, 0.1]:
        task = invoke_async(
            "experiment.py",
            "run_experiment",
            kwargs={"hyperparams": {"learning_rate": lr}, "seed": seed},
            gpu="a100"
        )
        tasks.append(task)

results = [task.get_result() for task in tasks]
```

## Data Patterns

Pass paths, not data:

```python
def process_data(input_path: str, output_path: str) -> dict:
    df = pd.read_parquet(input_path)
    # Process
    df.to_parquet(output_path)
    return {"rows": len(df), "output": output_path}
```

Return references:

```python
def generate_embeddings(text_file: str) -> dict:
    embeddings = compute_embeddings(text_file)
    np.save("/tmp/embeddings.npy", embeddings)
    return {
        "path": "/tmp/embeddings.npy",
        "shape": embeddings.shape
    }
```

## Error Handling

Serialization failures provide actionable guidance:

```python
invoke("process.py", "analyze", args=[numpy_array])
# TypeError: Cannot serialize arguments. Save to disk and pass path.
```

Remote exceptions propagate with full context:

```python
invoke("module.py", "buggy_function")
# RuntimeError: Remote execution failed: ValueError: Something went wrong
```

## Implementation

1. Generate wrapper script that imports module and calls function
2. Submit wrapper as Flow task with resources
3. Capture return value via temporary JSON file
4. Deserialize and return result

Clean separation enables:
- Local testing without mocks
- IDE autocomplete
- Easy refactoring
- No decorator pollution