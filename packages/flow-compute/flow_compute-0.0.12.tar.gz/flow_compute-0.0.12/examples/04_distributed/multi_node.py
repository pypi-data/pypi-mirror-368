#!/usr/bin/env python3
"""Multi-node distributed training example.

Demonstrates multi-node PyTorch training with manual node coordination.

Required environment variables (must be set in TaskConfig):
- FLOW_NODE_RANK: Node index (0, 1, ...)
- FLOW_NUM_NODES: Total node count
- FLOW_MAIN_IP: IP address of rank 0 node

Usage:
    # This example shows configuration for node 0
    # You must launch each node separately with its specific rank
    python 03_multi_node_training.py

Configuration:
- Instance type: h100-80gb.sxm.8x (8x H100 80GB per node)
- Node count: 2 nodes = 16 GPUs total
- Storage: 100GB volume for checkpoints

Note: For simpler setup, consider single-node multi-GPU training instead.
See examples/configs/single_node_multi_gpu.yaml
"""

import flow
from flow import TaskConfig, Flow
import os
import sys


def main():
    """Launch multi-node distributed training."""
    # Multi-node training script
    training_script = """#!/bin/bash
set -e

# Verify required environment variables
if [[ -z "${FLOW_NODE_RANK}" || -z "${FLOW_NUM_NODES}" || -z "${FLOW_MAIN_IP}" ]]; then
    echo "ERROR: Required environment variables not set"
    echo "Set FLOW_NODE_RANK, FLOW_NUM_NODES, and FLOW_MAIN_IP in TaskConfig"
    exit 1
fi

echo "=== Multi-Node Training Setup ==="
echo "Node rank: ${FLOW_NODE_RANK}"
echo "Total nodes: ${FLOW_NUM_NODES}"
echo "Main node IP: ${FLOW_MAIN_IP}"

# Install dependencies
echo "Installing PyTorch..."
pip install torch torchvision

# Create training script
cat > train_distributed.py << 'EOF'
import os
import time
import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

# Get Flow environment variables
node_rank = int(os.environ.get("FLOW_NODE_RANK", 0))
num_nodes = int(os.environ.get("FLOW_NUM_NODES", 1))
main_ip = os.environ.get("FLOW_MAIN_IP", "localhost")

# Setup distributed training
os.environ["MASTER_ADDR"] = main_ip
os.environ["MASTER_PORT"] = "29500"
os.environ["WORLD_SIZE"] = str(num_nodes * 8)  # 8 GPUs per node
os.environ["RANK"] = str(node_rank * 8 + int(os.environ.get("LOCAL_RANK", 0)))

# Initialize process group
dist.init_process_group(backend="nccl")
local_rank = int(os.environ.get("LOCAL_RANK", 0))
torch.cuda.set_device(local_rank)

rank = dist.get_rank()
world_size = dist.get_world_size()
print(f"Initialized rank {rank}/{world_size}, node {node_rank}/{num_nodes}")

# Create a simple model
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(1024, 2048),
            nn.ReLU(),
            nn.Linear(2048, 2048),
            nn.ReLU(),
            nn.Linear(2048, 10)
        )
    
    def forward(self, x):
        return self.layers(x)

# Initialize model
model = SimpleModel().cuda()
model = DDP(model, device_ids=[local_rank])
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training loop
if rank == 0:
    print("\\nStarting distributed training...")
    print(f"Total GPUs: {world_size}")
    print(f"Nodes: {num_nodes}")
    print(f"GPUs per node: {world_size // num_nodes}")

for epoch in range(10):
    # Simulated training step
    batch_size = 32
    data = torch.randn(batch_size, 1024).cuda()
    target = torch.randint(0, 10, (batch_size,)).cuda()
    
    # Forward pass
    output = model(data)
    loss = nn.CrossEntropyLoss()(output, target)
    
    # Backward pass
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    # Gather loss from all ranks
    all_losses = [torch.zeros(1).cuda() for _ in range(world_size)]
    dist.all_gather(all_losses, loss.detach())
    
    if rank == 0:
        avg_loss = sum([l.item() for l in all_losses]) / world_size
        print(f"Epoch {epoch}: average loss = {avg_loss:.4f}")
        
        # Save checkpoint
        if epoch % 5 == 0:
            checkpoint_path = f"/volumes/checkpoints/model_epoch_{epoch}.pt"
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.module.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': avg_loss,
            }, checkpoint_path)
            print(f"Saved checkpoint: {checkpoint_path}")
    
    # Synchronize all processes
    dist.barrier()
    time.sleep(0.5)  # Simulate more work

# Cleanup
dist.destroy_process_group()
print(f"Node {node_rank}, Rank {rank} finished successfully")
EOF

# Create checkpoint directory
mkdir -p /volumes/checkpoints

# Launch training with torchrun
echo "\\nLaunching training with torchrun..."
torchrun \\
    --nproc_per_node=8 \\
    --nnodes=${FLOW_NUM_NODES} \\
    --node_rank=${FLOW_NODE_RANK} \\
    --master_addr=${FLOW_MAIN_IP} \\
    --master_port=29500 \\
    train_distributed.py

echo "\\nTraining completed on node ${FLOW_NODE_RANK}"
"""

    # Configure multi-node task
    # NOTE: You must set FLOW_NODE_RANK differently for each node
    config = TaskConfig(
        name="multi-node-training",
        unique_name=True,
        instance_type="h100-80gb.sxm.8x",  # 8x H100 GPUs per node
        region="us-central1-b",
        num_instances=2,  # Launch 2 nodes = 16 GPUs total
        max_price_per_hour=20.0,  # Total for all nodes
        command=training_script,
        env={
            # These must be configured per node:
            "FLOW_NODE_RANK": "0",  # Set to 0 for first node, 1 for second
            "FLOW_NUM_NODES": "2",
            "FLOW_MAIN_IP": "CONFIGURE_ME",  # Set to rank 0 node's IP
        },
        volumes=[{"name": "checkpoints", "size_gb": 100}],
    )

    print("Multi-node distributed training configuration")
    print(f"Nodes: {config.num_instances}")
    print(f"Instance type: {config.instance_type} (8 GPUs per node)")
    print(f"Total GPUs: {config.num_instances * 8}")
    print()

    if config.env.get("FLOW_MAIN_IP") == "CONFIGURE_ME":
        print("ERROR: You must configure FLOW_MAIN_IP with the rank 0 node's IP")
        print("\nFor multi-node training:")
        print("1. Launch rank 0 node first and get its IP")
        print("2. Update FLOW_MAIN_IP in this script")
        print("3. Set FLOW_NODE_RANK=1 for the second node")
        print("4. Launch second node")
        return 1

    try:
        # Submit task
        task = flow.run(config)

        print(f"Task submitted successfully!")
        print(f"Task ID: {task.task_id}")
        print("\nMonitoring training progress...")

        # Stream logs
        print("\n=== Training Logs ===")
        for line in task.logs(follow=True):
            print(line, end="")

        # Wait for completion
        task.wait()

        # Check final status
        status = task.status
        if status == "completed":
            print("\n\nMulti-node training completed successfully!")
            print("\nCheckpoints saved to volume 'checkpoints'")
            return 0
        else:
            print(f"\n\nTraining failed with status: {status}")
            return 1

    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
