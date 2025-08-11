# Invoke Best Practices

## Principles

1. **Pure functions**: No side effects, clear inputs/outputs
2. **Type hints**: Aid debugging and validation
3. **Path-based data**: Pass paths, not objects
4. **Return metadata**: Summary info, not raw data
5. **Test locally**: Verify before remote execution

## Function Design

Pure functions with explicit dependencies:

```python
def train_model(
    data_path: str,
    config: Dict[str, float],
    output_dir: str
) -> Dict[str, float]:
    """Train model with given configuration."""
    import torch
    data = pd.read_parquet(data_path)
    model = create_model(config)
    metrics = train(model, data)
    torch.save(model.state_dict(), f"{output_dir}/model.pt")
    return {
        "accuracy": metrics["accuracy"],
        "loss": metrics["loss"],
        "model_path": f"{output_dir}/model.pt"
    }
```

Avoid global state and side effects.

## Data Handling

Pass paths, not data:

```python
def process_dataset(
    input_path: str,
    output_path: str,
    chunk_size: int = 1000
) -> Dict[str, any]:
    """Process large dataset in chunks."""
    total_rows = 0
    for chunk in pd.read_csv(input_path, chunksize=chunk_size):
        processed = transform(chunk)
        mode = 'w' if total_rows == 0 else 'a'
        processed.to_csv(output_path, mode=mode, header=(total_rows == 0))
        total_rows += len(chunk)
    
    return {
        "rows_processed": total_rows,
        "output_path": output_path,
        "output_size_mb": os.path.getsize(output_path) / 1e6
    }
```

## Error Handling

Validate inputs and provide context:

```python
def analyze_experiment(
    experiment_id: str,
    metrics_path: str
) -> Dict[str, float]:
    """Analyze experiment results."""
    if not experiment_id:
        raise ValueError("experiment_id cannot be empty")
    
    if not os.path.exists(metrics_path):
        raise FileNotFoundError(f"Metrics file not found: {metrics_path}")
    
    with open(metrics_path) as f:
        metrics = json.load(f)
    
    required_keys = ["accuracy", "loss", "f1_score"]
    missing = [k for k in required_keys if k not in metrics]
    if missing:
        raise KeyError(f"Missing required metrics: {missing}")
    
    return {
        "mean_accuracy": metrics["accuracy"],
        "improvement": metrics["accuracy"] - baseline
    }
```

## Configuration

Explicit config with validation:

```python
def run_experiment(config: Dict[str, Any]) -> Dict[str, Any]:
    """Run experiment with explicit configuration."""
    required = ["model_type", "data_path", "hyperparams"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError(f"Missing config keys: {missing}")
    
    model = create_model(config["model_type"], config["hyperparams"])
    results = train(model, config["data_path"])
    
    save_path = f"{config.get('output_dir', '/tmp')}/model.pt"
    torch.save(model, save_path)
    
    return {
        "config": config,
        "results": results,
        "artifacts": {"model": save_path}
    }
```

## Resource Management

Clean up temporary resources:

```python
@contextmanager
def temporary_directory():
    """Create and clean up temporary directory."""
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)

def process_with_cleanup(input_path: str, output_path: str) -> Dict[str, Any]:
    """Process data with proper cleanup."""
    with temporary_directory() as temp_dir:
        temp_file = f"{temp_dir}/intermediate.pkl"
        data = load_data(input_path)
        intermediate = transform(data)
        intermediate.to_pickle(temp_file)
        final = post_process(temp_file)
        final.to_parquet(output_path)
    return {"output_path": output_path, "rows": len(final)}
```

## Common Patterns

### Batch Processing

```python
def process_batch(
    batch_ids: List[str],
    input_dir: str,
    output_dir: str
) -> Dict[str, Any]:
    """Process multiple items in batch."""
    results = []
    for batch_id in batch_ids:
        data = load_json(f"{input_dir}/{batch_id}.json")
        processed = transform(data)
        output_path = f"{output_dir}/{batch_id}_processed.json"
        save_json(processed, output_path)
        results.append({"id": batch_id, "output": output_path})
    
    return {
        "batch_size": len(batch_ids),
        "results": results
    }
```

### Checkpointing

```python
def train_with_checkpoints(
    data_path: str,
    checkpoint_dir: str,
    resume_from: Optional[str] = None
) -> Dict[str, Any]:
    """Training with checkpoint support."""
    if resume_from and os.path.exists(resume_from):
        checkpoint = torch.load(resume_from)
        model = checkpoint["model"]
        start_epoch = checkpoint["epoch"]
    else:
        model = create_model()
        start_epoch = 0
    
    for epoch in range(start_epoch, max_epochs):
        metrics = train_epoch(model, data_path)
        if metrics["accuracy"] > best_accuracy:
            checkpoint_path = f"{checkpoint_dir}/epoch_{epoch}.pt"
            torch.save({"model": model, "epoch": epoch}, checkpoint_path)
    
    return {"final_epoch": epoch, "checkpoint": checkpoint_path}
```

### Parallel Processing

```python
def process_parallel(
    file_list: List[str],
    num_workers: int = 4
) -> Dict[str, Any]:
    """Process files in parallel."""
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(process_single, file_list))
    return {"total_files": len(file_list), "results": results}
```

## Testing Strategy

Test locally before remote execution:

```python
def test_train_model_locally():
    """Test function works before remote execution."""
    test_data = create_test_dataset()
    test_data.to_csv("/tmp/test_data.csv")
    
    result = train_model(
        data_path="/tmp/test_data.csv",
        config={"lr": 0.01},
        output_dir="/tmp/test_output"
    )
    
    assert "accuracy" in result
    assert 0 <= result["accuracy"] <= 1
    assert os.path.exists(result["model_path"])
```

## Performance

Stream large data efficiently:

```python
def process_efficiently(
    data_url: str,
    sample_rate: float = 1.0
) -> Dict[str, Any]:
    """Process data efficiently."""
    if data_url.startswith("s3://"):
        fs = s3fs.S3FileSystem()
        dataset = pq.ParquetDataset(data_url, filesystem=fs)
        if sample_rate < 1.0:
            sampled_pieces = random.sample(
                dataset.pieces, 
                int(len(dataset.pieces) * sample_rate)
            )
            df = pq.read_multiple_files(sampled_pieces, filesystem=fs)
        else:
            df = dataset.read_pandas()
    else:
        df = pd.read_parquet(data_url)
        if sample_rate < 1.0:
            df = df.sample(frac=sample_rate)
    
    return {"processed_rows": len(df), "results": analyze(df)}
```

## Debugging

Add strategic logging:

```python
def complex_function(input_path: str) -> Dict[str, Any]:
    logger = logging.getLogger(__name__)
    logger.info(f"Processing {input_path}")
    
    for step in ["load", "transform", "save"]:
        logger.info(f"Step: {step}")
        # Execute step
    
    return results
```

Use assertions for invariants:

```python
def robust_function(input_path: str, threshold: float) -> Dict[str, Any]:
    assert os.path.exists(input_path), f"Input not found: {input_path}"
    assert 0 <= threshold <= 1, f"Invalid threshold: {threshold}"
    
    data = load_data(input_path)
    assert len(data) > 0, "Empty dataset"
    
    results = process(data, threshold)
    assert "score" in results, "Missing score in results"
    
    return results
```