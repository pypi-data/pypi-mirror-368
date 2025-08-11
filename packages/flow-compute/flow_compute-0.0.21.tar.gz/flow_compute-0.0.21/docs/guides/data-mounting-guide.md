# Data Mounting Guide

## Overview

Flow SDK provides powerful data mounting capabilities for accessing datasets, models, and other resources in your GPU workloads. This guide covers the current data mounting features available through the Flow client's `submit()` API.

## Quick Start

Mount data from S3 or volumes with a single parameter:

```python
from flow import Flow

# Mount a single data source at /data
with Flow() as client:
    task = client.submit(
        "python train.py --data /data",
        gpu="a100",
        mounts="s3://my-bucket/datasets/imagenet"
    )

# Mount multiple data sources
with Flow() as client:
    task = client.submit(
        "python train.py",
        gpu="a100:4",
        mounts={
            "/datasets": "s3://my-bucket/datasets/imagenet",
            "/models": "volume://pretrained-models",
            "/cache": "volume://build-cache"
        }
    )
```

## Supported Data Sources

### 1. S3 Buckets

Mount S3 buckets and prefixes as read-only filesystems:

```python
# Mount entire bucket
mounts="s3://my-bucket"

# Mount specific prefix
mounts="s3://my-bucket/datasets/train"

# Multiple S3 sources
mounts={
    "/train": "s3://my-bucket/datasets/train",
    "/val": "s3://my-bucket/datasets/val",
    "/test": "s3://my-bucket/datasets/test"
}
```

**Requirements:**
- AWS credentials in environment (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- Read access to the specified bucket
- Credentials are automatically passed to the container

### 2. Volumes

Mount persistent block storage volumes:

```python
# Mount existing volume by name
mounts="volume://my-datasets"

# Mount existing volume by ID
mounts="volume://vol_abc123def456"

# Multiple volumes
mounts={
    "/datasets": "volume://training-data",
    "/checkpoints": "volume://model-checkpoints",
    "/outputs": "volume://results"
}
```

**Features:**
- Auto-creation: If a named volume doesn't exist, it's created with 100GB
- Persistence: Data persists across task runs
- Performance: High IOPS for database workloads

### 3. Local Files (Development)

For development, mount local directories:

```python
# Mount local directory
mounts="/home/user/datasets/imagenet"

# Multiple local paths
mounts={
    "/data": "/home/user/datasets",
    "/config": "/home/user/configs"
}
```

**Note:** Local paths must exist and be absolute.

## How It Works

### S3 Mounting

S3 data is mounted using s3fs-fuse with these characteristics:
- **Read-only**: Prevents accidental modifications
- **Cached**: Local caching for performance
- **Lazy loading**: Files downloaded on first access
- **Transparent**: Appears as regular filesystem

The SDK automatically:
1. Installs s3fs in the container
2. Configures AWS credentials
3. Mounts at specified paths
4. Validates mount success

### Volume Mounting

Volumes are attached as block devices:
- **Read-write**: Full filesystem access
- **Formatted**: Ext4 filesystem
- **Persistent**: Survives task termination
- **Fast**: NVMe-backed storage

The SDK handles:
1. Volume creation if needed
2. Attachment to instance
3. Formatting (first use only)
4. Mounting at specified path

## Examples

### Training with S3 Dataset

```python
# Train model on ImageNet from S3
with Flow() as client:
    task = client.submit(
        """
        python train.py \
            --data-dir /datasets/imagenet \
            --output-dir /outputs \
            --epochs 90
        """,
        gpu="a100:8",
        mounts={
            "/datasets": "s3://ml-datasets/imagenet",
            "/outputs": "volume://training-outputs"
        }
    )

    # Monitor progress
    task.logs(follow=True)
```

### Distributed Training with Shared Storage

```python
# Multi-node training with shared model storage
with Flow() as client:
    task = client.submit(
        """
        torchrun --nproc_per_node=8 \
            train_ddp.py \
            --data /data \
            --checkpoint-dir /checkpoints
        """,
        gpu="a100:8",
        num_instances=4,
        mounts={
            "/data": "s3://datasets/imagenet",
            "/checkpoints": "volume://ddp-checkpoints"
        }
    )
```

### Model Serving with Cached Models

```python
# Serve model with persistent model cache
with Flow() as client:
    task = client.submit(
        """
        python -m transformers_server \
            --model-dir /models \
            --port 8080
        """,
        gpu="a100",
        mounts={
            "/models": "volume://model-zoo"
        },
        ports=[8080]
    )
```

### Data Preprocessing Pipeline

```python
# Process raw data and save to volume
with Flow() as client:
    task = client.submit(
        """
        python preprocess.py \
            --input /raw-data \
            --output /processed-data \
            --num-workers 32
        """,
        instance_type="cpu-optimized",
        mounts={
            "/raw-data": "s3://raw-datasets/video-frames",
            "/processed-data": "volume://processed-datasets"
        }
    )
```

## Best Practices

### 1. Choose the Right Storage

- **S3**: Large, read-only datasets (training data, reference data)
- **Volumes**: Read-write data (checkpoints, outputs, caches)
- **Local**: Development and testing only

### 2. Optimize Performance

```python
# Good: Mount only needed data
mounts={"/data": "s3://bucket/train/shard-001"}

# Bad: Mount entire bucket when you need one file
mounts={"/data": "s3://bucket"}
```

### 3. Handle Credentials Securely

```python
# Set credentials in environment (not in code)
import os
os.environ["AWS_ACCESS_KEY_ID"] = "your-key"      # From secure source
os.environ["AWS_SECRET_ACCESS_KEY"] = "secret"    # From secure source

# Then submit task
with Flow() as client:
    task = client.submit(
        "python train.py",
        mounts="s3://private-bucket/data"
    )
```

### 4. Use Descriptive Names

```python
# Good: Clear, purposeful names
mounts={
    "/datasets": "volume://imagenet-2012-train",
    "/models": "volume://resnet50-pretrained",
    "/outputs": "volume://experiment-42-results"
}

# Bad: Generic names
mounts={
    "/data1": "volume://stuff",
    "/data2": "volume://more-stuff"
}
```

## Troubleshooting

### S3 Access Denied

```python
# Error: Access denied to S3 bucket
# Solution: Check AWS credentials
assert os.environ.get("AWS_ACCESS_KEY_ID"), "Missing AWS_ACCESS_KEY_ID"
assert os.environ.get("AWS_SECRET_ACCESS_KEY"), "Missing AWS_SECRET_ACCESS_KEY"

# Verify bucket access locally first
import boto3
s3 = boto3.client('s3')
s3.list_objects_v2(Bucket='your-bucket', MaxKeys=1)
```

### Volume Not Found

```python
# Error: Volume 'my-data' not found
# Solution: Let Flow create it automatically
with Flow() as client:
    task = client.submit(
        "python train.py",
        mounts="volume://my-data"  # Auto-creates with 100GB
    )

# Or create explicitly with custom size
with Flow() as client:
    volume = client.create_volume(size_gb=500, name="my-data")
```

### Mount Path Conflicts

```python
# Error: Mount path /data already in use
# Solution: Use unique mount paths
mounts={
    "/datasets": "s3://bucket/data",      # Good
    "/cache": "volume://cache",           # Good
    # "/data": "volume://another"         # Would conflict
}
```

## Advanced Usage

### Dynamic Volume Selection

```python
# Select volume based on availability
with Flow() as client:
    volumes = client.list_volumes()
    cache_volume = next(
        (v for v in volumes if v.name.startswith("cache-")), 
        None
    )

if cache_volume:
    mounts = {"/cache": f"volume://{cache_volume.volume_id}"}
else:
    mounts = {"/cache": "volume://cache-new"}  # Auto-create

with Flow() as client:
    task = client.submit("python process.py", mounts=mounts)
```

### Conditional Mounting

```python
# Mount data based on job type
job_type = "training"  # or "inference"

mounts = {
    "/models": "volume://model-zoo"  # Always mount models
}

if job_type == "training":
    mounts["/datasets"] = "s3://ml-datasets/imagenet"
    mounts["/checkpoints"] = "volume://training-checkpoints"
else:
    mounts["/outputs"] = "volume://inference-results"

with Flow() as client:
    task = client.submit(f"python {job_type}.py", mounts=mounts, gpu="a100")
```

## Limitations

Current limitations of data mounting (as of v0.5.0):

1. **Read-only S3**: Cannot write back to S3 directly
2. **No cross-region**: Volumes must be in same region as compute
3. **Submit API only**: Not available in `flow.run()` or CLI yet
4. **URL types**: Only S3 and volumes (no HTTP/Git yet)

## Future Enhancements

Planned improvements for data mounting:

- HTTP/HTTPS URL support for downloading models
- Git repository mounting for code
- Write-back to S3 with lifecycle policies
- Cross-region volume replication
- Integration with `flow run` and CLI commands

## Summary

Data mounting in Flow SDK provides a simple, powerful way to access data in GPU workloads:

- **Simple API**: Just add `mounts` parameter
- **Automatic setup**: No manual configuration needed
- **High performance**: Optimized for ML workloads
- **Secure**: Credentials handled safely
- **Flexible**: Mix and match data sources

Start with the `submit()` API today and seamlessly access your data in the cloud.