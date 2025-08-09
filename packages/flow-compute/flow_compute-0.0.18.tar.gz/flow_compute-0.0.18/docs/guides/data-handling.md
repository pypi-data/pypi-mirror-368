# Data Handling

Flow SDK provides multiple data access patterns for GPU workloads.

## Data Access Methods

### submit() - Automatic Mounting

```python
from flow import Flow

# Single source
with Flow() as client:
    task = client.submit(
        "python train.py --data /data",
        gpu="a100",
        mounts="s3://my-bucket/dataset"
    )

# Multiple sources
with Flow() as client:
    task = client.submit(
        "python train.py",
        gpu="a100:4",
        mounts={
            "/train": "s3://datasets/train",
            "/val": "s3://datasets/validation",
            "/models": "volume://pretrained-models"
        }
    )
```

Supported URLs:
- `s3://bucket/path` - S3 buckets (read-only)
- `volume://name` - Persistent volumes (read-write)

### run() - Explicit Volumes

```python
from flow import TaskConfig, VolumeSpec

config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    volumes=[
        VolumeSpec(size_gb=100, mount_path="/data"),
        VolumeSpec(volume_id="vol_abc123", mount_path="/models")
    ]
)
task = flow.run(config)
```

### invoke() - Path Arguments

```python
result = invoke(
    "process.py",
    "analyze_data",
    args=["s3://bucket/input.csv", "/tmp/output.csv"],
    gpu="a100"
)
```

### CLI - YAML Configuration

```yaml
# training.yaml
volumes:
  - name: datasets
    size_gb: 500
    mount_path: /data
```

## Patterns

### Pre-staged Volumes

For frequently accessed datasets:

```python
# One-time setup
with Flow() as client:
    volume = client.create_volume(size_gb=1000, name="imagenet-data")

# Reuse across tasks
config = TaskConfig(
    command="python train.py",
    volumes=[{"name": "imagenet-data", "mount_path": "/data"}]
)
```

### S3 Direct Access

For read-only datasets:

```python
with Flow() as client:
    task = client.submit(
        "python inference.py",
        mounts="s3://public-datasets/imagenet"
    )
```

### Dynamic Data Transfer

For pipeline outputs:

```python
# Generate data
preprocess = flow.run(TaskConfig(
    command="python preprocess.py --output /data/processed",
    volumes=[VolumeSpec(size_gb=100, mount_path="/data", name="exp-001")]
))

# Use processed data
train = flow.run(TaskConfig(
    command="python train.py --input /data/processed",
    volumes=[{"name": "exp-001", "mount_path": "/data"}]
))
```

### Ephemeral Storage

For temporary computations:

```python
config = TaskConfig(
    command="python process.py",
    volumes=[VolumeSpec(size_gb=500, mount_path="/scratch")]
)
```

## Performance

### Volume Locality

```python
# Match volume and instance regions
config = TaskConfig(
    instance_type="a100",
    region="us-west-2",
    volumes=[{"volume_id": "vol_abc123", "mount_path": "/data"}]
)
```

### S3 Caching

```python
# First access downloads, subsequent use cache
with Flow() as client:
    task = client.submit(
        """
        ls -la /data/  # Triggers download
        python train.py --data /data  # Uses cache
        """,
        mounts="s3://datasets/imagenet"
    )
```

### Docker Layer Cache

```python
config = TaskConfig(
    command="docker build .",
    volumes=[{
        "name": "docker-cache",
        "size_gb": 50,
        "mount_path": "/var/lib/docker"
    }]
)
```

## Security

### Credentials

```python
# Pass via environment
with Flow() as client:
    task = client.submit(
        "python train.py",
        env={
        "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
        "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"]
    },
    data="s3://private-bucket/data"
)
```

### Access Control

- Volumes are project-scoped
- S3 access respects IAM permissions
- Tasks have isolated filesystems

## Common Scenarios

### Large Dataset Training

```python
# Option A: Pre-staged volume
with Flow() as client:
    volume = client.create_volume(size_gb=2000, name="imagenet")
task = flow.run(TaskConfig(
    command="python train.py",
    volumes=[{"name": "imagenet", "mount_path": "/data"}]
))

# Option B: Stream from S3
with Flow() as client:
    task = client.submit(
        "python train.py --data /data",
        mounts="s3://ml-datasets/imagenet",
        gpu="a100:8"
    )
```

### Model Serving

```python
with Flow() as client:
    model_volume = client.create_volume(size_gb=100, name="model-zoo")
serving_config = TaskConfig(
    command="python -m model_server --port 8080",
    volumes=[{"name": "model-zoo", "mount_path": "/models"}],
    ports=[8080]
)
```

### Data Pipeline

```python
# Stage 1: Download
with Flow() as client:
    download = client.submit(
        "aws s3 sync s3://raw-data /data/raw",
        mounts={"/data": "volume://pipeline-data"}
    )

    # Stage 2: Process
    process = client.submit(
        "python process.py --input /data/raw --output /data/processed",
        mounts={"/data": "volume://pipeline-data"}
    )

    # Stage 3: Train
    train = client.submit(
        "python train.py --data /data/processed",
        mounts={"/data": "volume://pipeline-data"},
    gpu="a100:4"
)
```

### Distributed Training

```python
config = TaskConfig(
    command="torchrun --nproc_per_node=8 train_ddp.py",
    instance_type="a100:8",
    num_instances=4,
    volumes=[
        {"name": "training-data", "mount_path": "/data"},
        {"name": "checkpoints", "mount_path": "/checkpoints"}
    ]
)
```

## Storage Selection

| Use Case | Storage | Rationale |
|----------|---------|-----------|
| Training datasets | S3 → Volume | Stage once, reuse |
| Model checkpoints | Volume | Fast read/write |
| Temporary files | Ephemeral | Auto-cleanup |
| Shared datasets | S3 | No duplication |
| Experiment outputs | Named volumes | Easy tracking |

## Best Practices

1. **Minimize data movement** - Process data where it lives
2. **Right-size volumes** - Avoid overprovisioning
3. **Clean up resources** - Delete unused volumes
4. **Match regions** - Colocate compute and data
5. **Use appropriate storage** - S3 for read, volumes for write