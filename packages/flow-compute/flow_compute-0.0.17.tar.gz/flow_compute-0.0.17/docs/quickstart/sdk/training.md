# Train a Model in 5 Minutes

Run distributed training on GPUs with production-ready patterns.

## Prerequisites
- Flow SDK installed: `pip install flow-sdk`
- API key configured: `flow init`

## 1. Quick GPU Test (30 seconds)

```python
import flow
from flow import TaskConfig

# Verify PyTorch and GPU
config = TaskConfig(
    name="pytorch-test",
    command="python -c 'import torch; print(torch.cuda.get_device_name(0))'",
    instance_type="a100",
    max_run_time_seconds=30
)

flow_client = flow.Flow()
task = flow_client.run(config)
task.wait()
print(task.logs())
```

## 2. Complete Training Example (5 minutes)

### Save Training Script

Create `train.py`:

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import time
import json

# Define model
class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28*28, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 10)
        )
    
    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

# Training function
def train_epoch(dataloader, model, loss_fn, optimizer, device):
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)
        
        # Forward pass
        pred = model(X)
        loss = loss_fn(pred, y)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Stats
        total_loss += loss.item()
        correct += (pred.argmax(1) == y).type(torch.float).sum().item()
        total += y.size(0)
        
        if batch % 100 == 0:
            print(f"Batch {batch}: loss = {loss.item():.4f}")
    
    return total_loss / len(dataloader), correct / total

# Test function
def test(dataloader, model, loss_fn, device):
    model.eval()
    test_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
            total += y.size(0)
    
    avg_loss = test_loss / len(dataloader)
    accuracy = correct / total
    return avg_loss, accuracy

def main():
    # Device configuration
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
    
    # Hyperparameters
    batch_size = 64
    learning_rate = 1e-3
    epochs = 5
    
    # Data loading
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    print("Loading dataset...")
    train_data = datasets.FashionMNIST(
        root="data",
        train=True,
        download=True,
        transform=transform
    )
    test_data = datasets.FashionMNIST(
        root="data",
        train=False,
        transform=transform
    )
    
    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_data, batch_size=batch_size)
    
    # Initialize model
    model = NeuralNetwork().to(device)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    # Training metrics
    metrics = {
        "train_loss": [],
        "train_acc": [],
        "test_loss": [],
        "test_acc": [],
        "epoch_times": []
    }
    
    # Training loop
    print(f"\nStarting training for {epochs} epochs...")
    for epoch in range(epochs):
        start_time = time.time()
        
        print(f"\nEpoch {epoch+1}/{epochs}")
        print("-" * 50)
        
        # Train
        train_loss, train_acc = train_epoch(
            train_loader, model, loss_fn, optimizer, device
        )
        
        # Test
        test_loss, test_acc = test(test_loader, model, loss_fn, device)
        
        # Record metrics
        epoch_time = time.time() - start_time
        metrics["train_loss"].append(train_loss)
        metrics["train_acc"].append(train_acc)
        metrics["test_loss"].append(test_loss)
        metrics["test_acc"].append(test_acc)
        metrics["epoch_times"].append(epoch_time)
        
        print(f"Train Loss: {train_loss:.4f}, Acc: {train_acc:.3f}")
        print(f"Test Loss: {test_loss:.4f}, Acc: {test_acc:.3f}")
        print(f"Epoch Time: {epoch_time:.2f}s")
    
    # Save model
    torch.save(model.state_dict(), "model.pth")
    print(f"\nModel saved to model.pth")
    
    # Save metrics
    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print("Metrics saved to metrics.json")
    
    # Final results
    print(f"\nTraining completed!")
    print(f"Final test accuracy: {test_acc:.3f}")
    print(f"Total training time: {sum(metrics['epoch_times']):.2f}s")

if __name__ == "__main__":
    main()
```

### Run Training on GPU

```python
import flow
from flow import TaskConfig
from flow.errors import ResourceUnavailableError

# Upload and run the training script
training_config = TaskConfig(
    name="fashion-mnist-training",
    command="python train.py",
    instance_type="a100",
    max_run_time_hours=1,
    max_price_per_hour=3.50,
    # Code upload happens automatically when command references local files
)

try:
    flow_client = flow.Flow()
    task = flow_client.run(training_config, wait=True)
    print(f"Training task: {task.task_id}")
    print(f"Status: {task.status}")
    print(f"Cost per hour: {task.cost_per_hour}")
    
    # Stream training logs
    print("\nTraining logs:")
    for line in task.logs(follow=True):
        print(line, end='')
        if task.is_terminal:
            break
    
    # Final status
    task.refresh()
    print(f"\nFinal status: {task.status}")
    print(f"Total cost: {task.total_cost}")
    
    # SSH to download results (if needed)
    if task.is_running:
        print(f"\nTo download results:")
        print(f"1. SSH to instance: {task.ssh_command}")
        print(f"2. Copy files: scp <user>@<host>:/workspace/model.pth ./")
        
except ResourceUnavailableError as e:
    print(f"No GPU available: {e}")
    print("Try: different instance type or higher price limit")
except Exception as e:
    print(f"Training failed: {e}")
```

## 3. Distributed Training Example

### Multi-GPU Training Script

Create `distributed_train.py`:

```python
import os
import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

def setup_distributed():
    """Initialize distributed training."""
    dist.init_process_group("nccl")
    torch.cuda.set_device(int(os.environ["LOCAL_RANK"]))

def cleanup_distributed():
    """Clean up distributed training."""
    dist.destroy_process_group()

def train_distributed():
    # Setup
    setup_distributed()
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    device = torch.cuda.current_device()
    
    if rank == 0:
        print(f"Training on {world_size} GPUs")
    
    # Model
    model = nn.Sequential(
        nn.Linear(784, 256),
        nn.ReLU(),
        nn.Linear(256, 10)
    ).to(device)
    model = DDP(model, device_ids=[device])
    
    # Data with distributed sampler
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    dataset = datasets.MNIST("data", train=True, download=True, transform=transform)
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank)
    dataloader = DataLoader(dataset, batch_size=64, sampler=sampler)
    
    # Training
    optimizer = torch.optim.Adam(model.parameters())
    loss_fn = nn.CrossEntropyLoss()
    
    for epoch in range(5):
        sampler.set_epoch(epoch)  # Important for proper shuffling
        
        for batch_idx, (data, target) in enumerate(dataloader):
            data, target = data.to(device), target.to(device)
            data = data.view(data.size(0), -1)
            
            optimizer.zero_grad()
            output = model(data)
            loss = loss_fn(output, target)
            loss.backward()
            optimizer.step()
            
            if rank == 0 and batch_idx % 100 == 0:
                print(f"Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}")
    
    # Save from rank 0
    if rank == 0:
        torch.save(model.module.state_dict(), "distributed_model.pth")
        print("Model saved!")
    
    cleanup_distributed()

if __name__ == "__main__":
    train_distributed()
```

### Launch Distributed Training

```python
import flow
from flow import TaskConfig

# Multi-GPU configuration
distributed_config = TaskConfig(
    name="distributed-training",
    command="""
    # Install dependencies
    pip install torch torchvision
    
    # Run distributed training
    torchrun \
        --nproc_per_node=4 \
        --nnodes=1 \
        --node_rank=0 \
        --master_addr=localhost \
        --master_port=29500 \
        distributed_train.py
    """,
    instance_type="4xa100",  # 4 GPUs
    max_run_time_hours=2,
    max_price_per_hour=14.00
)

flow_client = flow.Flow()
task = flow_client.run(distributed_config, wait=True)
print(f"Distributed training: {task.task_id}")

# Monitor progress
for line in task.logs(follow=True, tail=100):
    print(line, end='')
    if "Model saved!" in line:
        break

print(f"\nTotal training cost: {task.total_cost}")
```

## 4. Training with Checkpoints

```python
import flow
from flow import TaskConfig

# Training with checkpoint support
checkpoint_script = '''
import torch
import os
from pathlib import Path

def save_checkpoint(state, checkpoint_dir="checkpoints"):
    Path(checkpoint_dir).mkdir(exist_ok=True)
    checkpoint_path = f"{checkpoint_dir}/checkpoint_epoch_{state['epoch']}.pth"
    torch.save(state, checkpoint_path)
    print(f"Checkpoint saved: {checkpoint_path}")
    
    # Save latest symlink
    latest_path = f"{checkpoint_dir}/latest.pth"
    if os.path.exists(latest_path):
        os.remove(latest_path)
    os.symlink(os.path.basename(checkpoint_path), latest_path)

def load_checkpoint(checkpoint_path, model, optimizer=None):
    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    if optimizer and 'optimizer_state_dict' in checkpoint:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    
    return checkpoint.get('epoch', 0)

# Training with checkpointing
def train_with_checkpoints():
    # ... model setup ...
    
    # Check for existing checkpoint
    start_epoch = 0
    checkpoint_path = "checkpoints/latest.pth"
    if os.path.exists(checkpoint_path):
        print(f"Resuming from {checkpoint_path}")
        start_epoch = load_checkpoint(checkpoint_path, model, optimizer)
    
    # Training loop
    for epoch in range(start_epoch, num_epochs):
        # ... training code ...
        
        # Save checkpoint every epoch
        save_checkpoint({
            'epoch': epoch + 1,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': loss,
        })
'''

# Run with checkpoint support
checkpoint_config = TaskConfig(
    name="training-with-checkpoints",
    command=f"python -c '{checkpoint_script}'",
    instance_type="a100",
    max_run_time_hours=4,
    max_price_per_hour=3.50,
    # Mount persistent volume for checkpoints
    volumes=[{
        "name": "training-checkpoints",
        "size_gb": 50,
        "mount_path": "/workspace/checkpoints"
    }]
)

flow_client = flow.Flow()
task = flow_client.run(checkpoint_config)
print(f"Training with checkpoints: {task.task_id}")
```

## 5. Cost Analysis

### Training Cost Estimates

| Workload | Dataset | Instance | Time | Cost |
|----------|---------|----------|------|------|
| Fashion-MNIST | 60K images | a100 | 5 min | ~$0.30 |
| ImageNet | 1.2M images | 8xa100 | 40 hrs | ~$1,120 |
| Custom CNN | 100K images | a100 | 2 hrs | ~$7.00 |
| Fine-tuning | 10K samples | a100 | 1 hr | ~$3.50 |

### Cost Optimization

```python
def estimate_training_cost(
    dataset_size: int,
    batch_size: int,
    epochs: int,
    time_per_batch_ms: float,
    instance_type: str,
    hourly_rate: float
) -> dict:
    """Estimate training cost before running."""
    total_batches = (dataset_size // batch_size) * epochs
    total_time_hours = (total_batches * time_per_batch_ms) / (1000 * 60 * 60)
    total_cost = total_time_hours * hourly_rate
    
    return {
        "total_batches": total_batches,
        "estimated_hours": round(total_time_hours, 2),
        "estimated_cost": round(total_cost, 2),
        "cost_per_epoch": round(total_cost / epochs, 2)
    }

# Example estimation
estimate = estimate_training_cost(
    dataset_size=50000,
    batch_size=32,
    epochs=10,
    time_per_batch_ms=50,  # Measure this
    instance_type="a100",
    hourly_rate=3.50
)
print(f"Estimated training cost: ${estimate['estimated_cost']}")
print(f"Time: {estimate['estimated_hours']} hours")
```

## 6. Monitoring & Logging

```python
import flow
from flow import TaskConfig

# Training with comprehensive logging
monitored_config = TaskConfig(
    name="monitored-training",
    command="""
    # Install monitoring tools
    pip install tensorboard wandb
    
    # Set up Weights & Biases
    wandb login $WANDB_API_KEY
    
    # Run training with logging
    python train.py \
        --log-interval 10 \
        --tensorboard-dir /workspace/runs \
        --wandb-project flow-training
    """,
    instance_type="a100",
    environment={
        "WANDB_API_KEY": "your-wandb-key"
    },
    max_run_time_hours=2,
    max_price_per_hour=3.50
)

flow_client = flow.Flow()
task = flow_client.run(monitored_config, wait=True)

# Stream logs and monitor metrics
print(f"Training task: {task.task_id}")
print(f"Monitor at: https://wandb.ai/your-team/flow-training")

for line in task.logs(follow=True):
    print(line, end='')
    # Parse and display key metrics
    if "loss:" in line.lower():
        # Could extract and plot metrics here
        pass
```

## Next Steps

- [Distributed Training Guide](../../guides/distributed-training.md) - Multi-node setups
- [Hyperparameter Tuning](../../guides/hyperparameter-tuning.md) - Parallel sweeps
- [Model Serving](../inference.md) - Deploy trained models
- [Cost Optimization](../../guides/cost-optimization.md) - Spot instances, scheduling

## Troubleshooting

### Common Issues

1. **"CUDA out of memory"**
   ```python
   # Reduce batch size
   batch_size = 32  # Instead of 64
   # Enable gradient accumulation
   accumulation_steps = 4
   ```

2. **"Module not found"**
   ```python
   # Install dependencies in command
   command = """
   pip install -r requirements.txt
   python train.py
   """
   ```

3. **Slow data loading**
   ```python
   # Increase workers
   DataLoader(dataset, num_workers=4, pin_memory=True)
   ```

4. **Training interrupted**
   - Use checkpointing (shown above)
   - Enable automatic resume
   - Use persistent volumes for state