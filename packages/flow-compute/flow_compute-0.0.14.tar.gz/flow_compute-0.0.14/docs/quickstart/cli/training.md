# CLI Training Quickstart

Train models efficiently using Flow's command-line interface.

## Prerequisites
- Flow CLI installed: `pip install flow-sdk`
- API key configured: `flow init`

## 1. Quick Training Example (5 minutes)

### Simple PyTorch Training

```bash
# Create training script
cat > train.py << 'EOF'
import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# Simple CNN model
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.max_pool2d(x, 2)
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

# Training setup
device = torch.device("cuda")
model = SimpleCNN().to(device)
optimizer = torch.optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss()

# Data loading
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])
train_dataset = datasets.MNIST('data', train=True, download=True, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

# Training loop
print(f"Training on {torch.cuda.get_device_name(0)}")
for epoch in range(5):
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        if batch_idx % 100 == 0:
            print(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}')

torch.save(model.state_dict(), 'model.pth')
print("Training complete! Model saved.")
EOF

# Run training on GPU
flow run \
    --name "mnist-training" \
    --instance-type "a100" \
    --max-runtime "30m" \
    --max-price 2.00 \
    --command "pip install torch torchvision && python train.py"

# Monitor training
flow logs mnist-training --follow
```

## 2. Distributed Training

### Multi-GPU Training Script

```bash
# Create distributed training script
cat > distributed_train.py << 'EOF'
import os
import torch
import torch.distributed as dist
import torch.nn as nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

def setup(rank, world_size):
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

def cleanup():
    dist.destroy_process_group()

def train(rank, world_size):
    setup(rank, world_size)
    
    # Model
    model = nn.Sequential(
        nn.Linear(784, 512),
        nn.ReLU(),
        nn.Linear(512, 512),
        nn.ReLU(),
        nn.Linear(512, 10)
    ).to(rank)
    model = DDP(model, device_ids=[rank])
    
    # Data with distributed sampler
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    dataset = datasets.MNIST('data', train=True, download=True, transform=transform)
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank)
    dataloader = DataLoader(dataset, batch_size=64, sampler=sampler)
    
    # Training
    optimizer = torch.optim.Adam(model.parameters())
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(10):
        sampler.set_epoch(epoch)
        for batch_idx, (data, target) in enumerate(dataloader):
            data = data.view(-1, 784).to(rank)
            target = target.to(rank)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            if rank == 0 and batch_idx % 100 == 0:
                print(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}')
    
    if rank == 0:
        torch.save(model.module.state_dict(), 'distributed_model.pth')
        print("Training complete!")
    
    cleanup()

if __name__ == "__main__":
    world_size = torch.cuda.device_count()
    torch.multiprocessing.spawn(train, args=(world_size,), nprocs=world_size)
EOF

# Run distributed training
flow run \
    --name "distributed-training" \
    --instance-type "4xa100" \
    --max-runtime "2h" \
    --command "
        pip install torch torchvision
        python distributed_train.py
    "
```

### Using torchrun

```bash
# Launch with torchrun for better distributed training
flow run \
    --name "torchrun-training" \
    --instance-type "8xa100" \
    --max-runtime "4h" \
    --command "
        pip install torch torchvision
        torchrun \
            --nproc_per_node=8 \
            --master_port=29500 \
            distributed_train.py
    "
```

## 3. Training with Checkpoints

### Checkpoint-enabled Training

```bash
# Create training with checkpointing
cat > train_with_checkpoints.sh << 'EOF'
#!/bin/bash

# Install dependencies
pip install torch torchvision tensorboard

# Python training script with checkpointing
python - << 'PYTHON_SCRIPT'
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import os
from datetime import datetime

class CheckpointTrainer:
    def __init__(self, model, checkpoint_dir="checkpoints"):
        self.model = model
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
        
    def save_checkpoint(self, epoch, optimizer, loss):
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': loss,
        }
        path = f"{self.checkpoint_dir}/checkpoint_epoch_{epoch}.pth"
        torch.save(checkpoint, path)
        print(f"Checkpoint saved: {path}")
        
        # Save as latest
        latest_path = f"{self.checkpoint_dir}/latest.pth"
        torch.save(checkpoint, latest_path)
    
    def load_checkpoint(self, optimizer, path=None):
        if path is None:
            path = f"{self.checkpoint_dir}/latest.pth"
        
        if os.path.exists(path):
            checkpoint = torch.load(path)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            print(f"Resumed from epoch {checkpoint['epoch']}")
            return checkpoint['epoch']
        return 0

# Model definition
model = nn.Sequential(
    nn.Conv2d(3, 64, 3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Conv2d(64, 128, 3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Flatten(),
    nn.Linear(128 * 8 * 8, 10)
).cuda()

# Training setup
optimizer = torch.optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss()
trainer = CheckpointTrainer(model)

# Data loading
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])
train_dataset = datasets.CIFAR10('data', train=True, download=True, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)

# Resume from checkpoint if exists
start_epoch = trainer.load_checkpoint(optimizer)

# Training loop
for epoch in range(start_epoch, 20):
    epoch_loss = 0
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.cuda(), target.cuda()
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        epoch_loss += loss.item()
        
        if batch_idx % 50 == 0:
            print(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}')
    
    # Save checkpoint every epoch
    avg_loss = epoch_loss / len(train_loader)
    trainer.save_checkpoint(epoch + 1, optimizer, avg_loss)

# Save final model
torch.save(model.state_dict(), 'final_model.pth')
print("Training complete!")
PYTHON_SCRIPT
EOF

# Run with checkpoint support and persistent storage
flow run \
    --name "checkpoint-training" \
    --instance-type "a100" \
    --max-runtime "4h" \
    --volume "name=training-checkpoints,size=50,mount=/workspace/checkpoints" \
    --download "/workspace/checkpoints/*" \
    --download "final_model.pth" \
    train_with_checkpoints.sh

# Resume if interrupted
flow run \
    --name "checkpoint-training-resume" \
    --instance-type "a100" \
    --max-runtime "4h" \
    --volume "name=training-checkpoints,mount=/workspace/checkpoints" \
    --upload "./checkpoints/*:/workspace/checkpoints/" \
    train_with_checkpoints.sh
```

## 4. Hyperparameter Sweep

### Parallel Hyperparameter Search

```bash
# Create sweep configuration
cat > sweep_config.json << 'EOF'
{
    "learning_rates": [0.001, 0.0001, 0.00001],
    "batch_sizes": [32, 64, 128],
    "hidden_sizes": [128, 256, 512]
}
EOF

# Sweep script
cat > hyperparameter_sweep.sh << 'EOF'
#!/bin/bash

# Read parameters
LR=$1
BATCH_SIZE=$2
HIDDEN_SIZE=$3

echo "Training with LR=$LR, Batch=$BATCH_SIZE, Hidden=$HIDDEN_SIZE"

# Run training with specific hyperparameters
python train.py \
    --lr $LR \
    --batch-size $BATCH_SIZE \
    --hidden-size $HIDDEN_SIZE \
    --output-dir "results/lr${LR}_bs${BATCH_SIZE}_hs${HIDDEN_SIZE}"

# Save metrics
echo "{\"lr\": $LR, \"batch_size\": $BATCH_SIZE, \"hidden_size\": $HIDDEN_SIZE}" > metrics.json
EOF

# Launch parallel sweep
for lr in 0.001 0.0001 0.00001; do
    for bs in 32 64 128; do
        for hs in 128 256 512; do
            flow run \
                --name "sweep-lr${lr}-bs${bs}-hs${hs}" \
                --instance-type "a100" \
                --max-runtime "1h" \
                --max-price 4.00 \
                --download "metrics.json" \
                --download "results/*" \
                --command "bash hyperparameter_sweep.sh $lr $bs $hs" &
        done
    done
done

# Wait for all jobs
wait

# Collect results
flow list --name "sweep-*" --format json > sweep_results.json
```

## 5. Custom Dataset Training

### Training with S3 Data

```bash
# Create data loading script
cat > train_s3_data.py << 'EOF'
import boto3
import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from PIL import Image
import io

class S3Dataset(Dataset):
    def __init__(self, bucket, prefix, csv_file):
        self.s3 = boto3.client('s3')
        self.bucket = bucket
        self.prefix = prefix
        self.df = pd.read_csv(f"s3://{bucket}/{csv_file}")
        
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        
        # Load image from S3
        key = f"{self.prefix}/{row['filename']}"
        obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        img = Image.open(io.BytesIO(obj['Body'].read()))
        
        # Transform and return
        return self.transform(img), row['label']

# Training with S3 data
dataset = S3Dataset('my-bucket', 'train-images', 'labels.csv')
dataloader = DataLoader(dataset, batch_size=32, num_workers=4)

# ... rest of training code ...
EOF

# Run training with S3 access
flow run \
    --name "s3-training" \
    --instance-type "a100" \
    --env "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" \
    --env "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" \
    --command "
        pip install torch torchvision boto3 pandas pillow
        python train_s3_data.py
    "
```

## 6. Training Monitoring

### TensorBoard Integration

```bash
# Launch training with TensorBoard
flow run \
    --name "monitored-training" \
    --instance-type "a100" \
    --ports 6006 \
    --max-runtime "4h" \
    --command "
        pip install torch tensorboard
        
        # Start TensorBoard in background
        tensorboard --logdir runs --host 0.0.0.0 &
        
        # Run training
        python train_with_tensorboard.py
    "

# Access TensorBoard
flow port-forward monitored-training 6006:6006
# Open http://localhost:6006 in browser
```

### Weights & Biases Integration

```bash
# Training with W&B
flow run \
    --name "wandb-training" \
    --instance-type "a100" \
    --env "WANDB_API_KEY=$WANDB_API_KEY" \
    --command "
        pip install torch wandb
        
        # Initialize W&B
        wandb login $WANDB_API_KEY
        
        # Run training with W&B logging
        python train_with_wandb.py \
            --project flow-training \
            --name experiment-1
    "
```

## 7. Cost-Optimized Training

### Spot Instance Training

```bash
# Use spot instances with automatic resume
cat > spot_training.sh << 'EOF'
#!/bin/bash

# Check if checkpoint exists
if [ -f "checkpoints/latest.pth" ]; then
    echo "Resuming from checkpoint"
    RESUME_FLAG="--resume checkpoints/latest.pth"
else
    echo "Starting fresh training"
    RESUME_FLAG=""
fi

# Run training
python train.py $RESUME_FLAG \
    --save-freq 100 \
    --checkpoint-dir checkpoints
EOF

# Launch on spot instance
flow run \
    --name "spot-training" \
    --instance-type "a100" \
    --spot \
    --max-interruptions 5 \
    --volume "name=checkpoints,mount=/workspace/checkpoints" \
    spot_training.sh
```

### Multi-Region Training

```bash
# Try multiple regions for better availability
REGIONS=("us-west-2" "us-east-1" "eu-west-1")

for region in "${REGIONS[@]}"; do
    flow run \
        --name "training-$region" \
        --instance-type "a100" \
        --region $region \
        --max-price 4.00 \
        --command "python train.py" && break
done
```

## 8. Training Pipelines

### Complete Training Pipeline

```bash
#!/bin/bash
# training_pipeline.sh - End-to-end training pipeline

# Step 1: Data preparation
echo "Preparing data..."
PREP_TASK=$(flow run \
    --name "data-prep" \
    --instance-type "cpu" \
    --command "python prepare_data.py" \
    --download "processed_data/*")

flow wait $PREP_TASK

# Step 2: Training
echo "Starting training..."
TRAIN_TASK=$(flow run \
    --name "model-training" \
    --instance-type "8xa100" \
    --upload "processed_data/*" \
    --command "python train.py --data processed_data" \
    --download "model.pth" \
    --download "metrics.json")

flow wait $TRAIN_TASK

# Step 3: Evaluation
echo "Evaluating model..."
EVAL_TASK=$(flow run \
    --name "model-eval" \
    --instance-type "a100" \
    --upload "model.pth" \
    --upload "test_data/*" \
    --command "python evaluate.py" \
    --download "evaluation_report.pdf")

flow wait $EVAL_TASK

# Step 4: Deploy if metrics pass threshold
METRICS=$(cat metrics.json)
ACCURACY=$(echo $METRICS | jq -r '.accuracy')

if (( $(echo "$ACCURACY > 0.95" | bc -l) )); then
    echo "Deploying model..."
    flow run \
        --name "model-deployment" \
        --instance-type "l40s" \
        --upload "model.pth" \
        --ports 8000 \
        --max-runtime "720h" \
        --command "python serve_model.py"
else
    echo "Model accuracy $ACCURACY below threshold"
fi
```

## Common Issues

### GPU Memory Management

```bash
# Monitor GPU memory during training
flow exec <task_id> -- nvidia-smi -l 1

# Reduce memory usage
flow run \
    --env "PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128" \
    --command "python train.py --gradient-accumulation 4"
```

### Debugging Failed Training

```bash
# Enable detailed logging
flow run \
    --name "debug-training" \
    --env "TORCH_CPP_LOG_LEVEL=INFO" \
    --env "CUDA_LAUNCH_BLOCKING=1" \
    --command "python train.py --debug"

# Interactive debugging
flow run \
    --interactive \
    --instance-type "a100" \
    --command "bash"
# Then manually run and debug
```

## Next Steps

- [CLI Fine-tuning Guide](fine-tuning.md) - Fine-tune pre-trained models
- [Distributed Training](../../guides/distributed-training.md) - Advanced multi-node
- [Training Best Practices](../../guides/training-best-practices.md) - Optimization tips
- [Cost Optimization](../../guides/cost-optimization.md) - Reduce training costs