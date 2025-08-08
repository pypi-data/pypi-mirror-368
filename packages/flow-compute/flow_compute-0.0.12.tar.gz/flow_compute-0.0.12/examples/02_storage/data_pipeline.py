#!/usr/bin/env python3
"""S3 data access example.

This example demonstrates how to:
1. Download data from S3 to persistent volumes
2. Use AWS CLI within Flow tasks
3. Manage datasets across training runs
4. Handle large-scale data efficiently

Prerequisites:
- Flow SDK installed (`pip install flow-sdk`)
- Mithril API key configured (`flow init`)
- AWS credentials (for S3 access)

How to run:
    # Set AWS credentials
    export AWS_ACCESS_KEY_ID=your_key
    export AWS_SECRET_ACCESS_KEY=your_secret

    # Run example
    python 04_s3_data_access.py

Note: Flow SDK currently handles S3 access through AWS CLI
within the task environment, not through direct mounting.
"""

import flow
from flow import TaskConfig, Flow
import os
import sys


def main():
    """Demonstrate S3 data access patterns."""

    # Check AWS credentials
    if not os.environ.get("AWS_ACCESS_KEY_ID"):
        print("ERROR: AWS credentials not found")
        print("\nPlease set AWS credentials:")
        print("  export AWS_ACCESS_KEY_ID=your_key")
        print("  export AWS_SECRET_ACCESS_KEY=your_secret")
        return 1

    # Example 1: Download S3 data to volume
    print("Example 1: Download S3 data to persistent volume")
    print("-" * 50)

    download_script = """#!/bin/bash
set -e

echo "=== S3 Data Download Example ==="

# Install AWS CLI
apt-get update && apt-get install -y awscli

# Create data directory
mkdir -p /volumes/data

# Download data from S3
echo "Downloading data from S3..."
aws s3 sync s3://my-bucket/dataset/ /volumes/data/ --no-sign-request || {
    echo "Note: Replace 's3://my-bucket/dataset/' with your actual S3 path"
    echo "Creating sample data instead..."
    echo "sample data" > /volumes/data/sample.txt
}

# Verify download
echo ""
echo "Data downloaded to /volumes/data:"
ls -la /volumes/data/
echo ""
echo "Total size:"
du -sh /volumes/data/
"""

    config = TaskConfig(
        name="s3-download",
        unique_name=True,
        instance_type="h100-80gb.sxm.8x",
        region="us-central1-b",
        command=download_script,
        volumes=[{"name": "data", "size_gb": 100}],
        # Pass AWS credentials to the task environment
        # Note: Tasks run in isolated environments and need credentials
        env={
            k: v
            for k, v in {
                "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
                "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
                "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            }.items()
            if v is not None
        },
    )

    try:
        task = flow.run(config)
        print(f"Task submitted: {task.task_id}")
        print("This task will download S3 data to a persistent volume")

        # Monitor task
        task.wait()
        print("\nTask completed. Data is now in volume 'data'")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    print("\n" + "=" * 70 + "\n")

    # Example 2: Training with S3 data
    print("Example 2: ML training with S3 data")
    print("-" * 50)

    training_script = """#!/bin/bash
set -e

echo "=== ML Training with S3 Data ==="

# Install dependencies
pip install torch torchvision boto3

# Python script for training
python3 << 'EOF'
import os
import torch
import boto3
from pathlib import Path

# Check if we have cached data
data_path = Path('/volumes/data')
if data_path.exists() and any(data_path.iterdir()):
    print(f"Using cached data from {data_path}")
    print(f"Files: {len(list(data_path.rglob('*')))} items")
else:
    print("No cached data found. Would download from S3 here.")
    # In real scenario, download data:
    # s3 = boto3.client('s3')
    # s3.download_file('bucket', 'key', '/volumes/data/file')

# Simulate training
print("\\nStarting training...")
model = torch.nn.Linear(10, 1)
optimizer = torch.optim.Adam(model.parameters())

for epoch in range(5):
    # Simulate training step
    data = torch.randn(32, 10)
    loss = model(data).mean()
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    print(f"Epoch {epoch}: loss = {loss.item():.4f}")

# Save model
model_path = '/volumes/models/model.pt'
os.makedirs(os.path.dirname(model_path), exist_ok=True)
torch.save(model.state_dict(), model_path)
print(f"\\nModel saved to {model_path}")
EOF
"""

    config = TaskConfig(
        name="s3-training",
        unique_name=True,
        instance_type="h100-80gb.sxm.8x",
        region="us-central1-b",
        command=training_script,
        volumes=[
            {"name": "data", "size_gb": 100},  # Reuse data from example 1
            {"name": "models", "size_gb": 20},  # Store trained models
        ],
        env={
            k: v
            for k, v in {
                "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
                "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
                "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            }.items()
            if v is not None
        },
    )

    try:
        task = flow.run(config)
        print(f"Training task submitted: {task.task_id}")
        print("\nThe task will:")
        print("  1. Use data from persistent volume (downloaded in Example 1)")
        print("  2. Train a model")
        print("  3. Save model to persistent volume")

        # Show logs
        print("\n=== Training Logs ===")
        for line in task.logs(follow=True):
            print(line, end="")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    print("\n" + "=" * 70 + "\n")

    # Example 3: Upload results to S3
    print("Example 3: Upload results back to S3")
    print("-" * 50)

    upload_script = """#!/bin/bash
set -e

echo "=== Upload Results to S3 ==="

# Install AWS CLI
apt-get update && apt-get install -y awscli

# Check for results
if [ -d "/volumes/models" ]; then
    echo "Found models to upload:"
    ls -la /volumes/models/
    
    # Upload to S3 (replace with your bucket)
    # aws s3 sync /volumes/models/ s3://my-bucket/results/
    echo "\\nWould upload to S3 here (uncomment the aws s3 sync line with your bucket)"
else
    echo "No models found to upload"
fi
"""

    config = TaskConfig(
        name="s3-upload",
        unique_name=True,
        instance_type="h100-80gb.sxm.8x",
        region="us-central1-b",
        command=upload_script,
        volumes=[{"name": "models"}],  # Access models from example 2
        env={
            k: v
            for k, v in {
                "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
                "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
                "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            }.items()
            if v is not None
        },
    )

    try:
        task = flow.run(config)
        print(f"Upload task submitted: {task.task_id}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
