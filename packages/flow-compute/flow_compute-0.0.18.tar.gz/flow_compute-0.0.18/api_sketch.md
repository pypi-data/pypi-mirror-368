# Flow SDK API Design

## Overview

Flow SDK provides the simplest way to run code on GPUs. Built on Domain-Driven Design principles, it offers a unified interface for GPU workload submission across heterogeneous cloud infrastructure while maintaining provider-agnostic abstractions.

### Core Philosophy
- **Simple by default**: One line to run on GPU
- **Progressive disclosure**: Complexity available when needed
- **Provider agnostic**: Clean abstractions over cloud specifics
- **Fail fast**: Validate early with clear errors
- **Zero magic**: Explicit behavior, predictable types

### Key Concepts
- **Tasks**: Units of work executed on GPU infrastructure - from simple commands to distributed training
- **Providers**: Cloud platform handlers (Mithril, Local, AWS/GCP/Azure planned)
- **Volumes**: Persistent storage that survives task completion
- **Instance Types**: GPU hardware specifications with simple naming ("a100", "8xh100")

## Architecture

### System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                        User API Layer                       │
│  Flow class    TaskConfig    Task    decorators    invoke   │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                      Core Domain Layer                      │
│  TaskEngine    InstanceMatcher    GPUParser    interfaces   │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                     Provider Layer (SPI)                    │
│  IProvider    IComputeProvider    IStorageProvider          │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                   Provider Implementations                  │
│     MithrilProvider       LocalProvider      Future Providers   │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **User API Layer**: High-level interfaces (Flow class, decorators)
2. **Core Domain**: Business logic and orchestration (TaskEngine, resource matching)
3. **Provider SPI**: Protocol-based interfaces for cloud abstraction
4. **Provider Implementations**: Cloud-specific adapters

## Core API

### Primary Interface

```python
from flow import Flow, TaskConfig, VolumeSpec

# Initialize client (auto-discovers configuration)
flow = Flow()

# Simple execution
task = flow.run("python train.py", instance_type="a100")

# Full configuration
config = TaskConfig(
    name="training-job",
    instance_type="8xh100",  # 8x H100 GPUs
    command=["python", "train.py", "--distributed"],
    image="pytorch/pytorch:2.1.0-cuda12.1-cudnn8",
    volumes=[
        VolumeSpec(size_gb=500, mount_path="/data", name="datasets")
    ],
    env={"BATCH_SIZE": "256"},
    max_price_per_hour=50.0,
    max_run_time_hours=24.0
)
task = flow.run(config)
```

### Task Lifecycle Management

```python
# Submit and get Task object
task = flow.run(config)

# Task object provides complete control
print(f"Task ID: {task.task_id}")
print(f"Status: {task.status}")  # PENDING → RUNNING → COMPLETED
print(f"Cost per hour: {task.cost_per_hour}")

# Wait for completion
task.wait(timeout=3600)  # 1 hour timeout

# Stream logs in real-time
for line in task.logs(follow=True):
    if "loss:" in line:
        print(line.strip())
    if task.is_terminal:
        break

# SSH access for debugging
if task.is_running:
    task.ssh()  # Interactive session
    task.ssh("nvidia-smi")  # Run command

# Graceful termination
task.cancel()
```

### Instance Discovery

```python
# Find available instances
instances = flow.find_instances({
    "gpu_memory_gb": 80,
    "max_price": 10.0,
    "region": "us-central1-b"
})

for inst in instances[:5]:
    print(f"{inst['instance_type']}: ${inst['price_per_hour']}/hr")
```

## Configuration Model

### TaskConfig

Primary configuration object with comprehensive validation:

```python
from flow import TaskConfig, VolumeSpec

config = TaskConfig(
    # Basic identification
    name="training-job",  # Alphanumeric + dash/underscore
    
    # Instance specification (exactly ONE required)
    instance_type="a100",        # Direct: "a100", "4xa100", "8xh100"
    # OR
    min_gpu_memory_gb=40,        # Capability-based selection
    
    # Command specification (optional - defaults to 'sleep infinity')
    command=["python", "train.py", "--epochs", "10"],  # List form
    # OR
    shell="cd /app && python train.py",                # Shell string
    # OR
    script="import torch\n...",                        # Script content
    
    # Environment
    image="pytorch/pytorch:2.1.0-cuda12.1-cudnn8",
    env={"WANDB_API_KEY": "...", "BATCH_SIZE": "256"},
    working_dir="/workspace",
    
    # Storage
    volumes=[
        VolumeSpec(size_gb=100, mount_path="/data", name="datasets"),
        VolumeSpec(volume_id="vol-abc123", mount_path="/checkpoints")
    ],
    
    # Constraints
    max_price_per_hour=10.0,      # Cost protection
    max_run_time_hours=24.0,      # Auto-termination
    region="us-central1-b",       # Location preference
    
    # Multi-node
    num_instances=1,              # Number of nodes
    
    # Access
    ssh_keys=["my-key"],          # SSH key names
    
    # Code upload
    upload_code=True              # Upload current directory
)
```

### VolumeSpec

Persistent storage specification:

```python
# Create new volume
VolumeSpec(
    name="training-data",         # Human-readable name
    size_gb=500,                  # Capacity
    mount_path="/data",           # Container mount point
    interface="block",            # Storage type (block/file)
    iops=3000                     # Performance tuning
)

# Attach existing volume
VolumeSpec(
    volume_id="vol-abc123",       # Existing volume ID
    mount_path="/data"            # Cannot specify size/iops
)
```

## Instance Type System

### Simple Naming

Flow uses intuitive instance type names:

```python
# Single GPU
"a100"      # 1x A100 80GB
"h100"      # 1x H100 80GB (or 8x based on provider default)

# Multi-GPU (count prefix)
"2xa100"    # 2x A100 80GB
"4xa100"    # 4x A100 80GB  
"8xa100"    # 8x A100 80GB
"8xh100"    # 8x H100 80GB
```

### Resolution System

```
User Input → Parser → Canonicalization → Provider Resolution → Instance Selection
"4xa100"   → count=4  → "a100-80gb.sxm.4x" → "it_fK7Cx6TVhOK5ZfXT" → Actual instance
           gpu=a100
```

### Capability-Based Selection

Let Flow find the best GPU:

```python
config = TaskConfig(
    min_gpu_memory_gb=40,     # Any GPU with 40GB+ VRAM
    max_price_per_hour=10.0   # Within budget
)
```

## Advanced Patterns

### Decorator Pattern

Function-based GPU execution:

```python
from flow import FlowApp

app = FlowApp()

@app.function(gpu="a100", memory=32768)
def train_model(data_path: str, epochs: int = 100):
    import torch
    # Training logic
    return {"accuracy": 0.95, "loss": 0.01}

# Remote execution
result = train_model.remote("s3://bucket/data", epochs=200)

# Local execution
local_result = train_model("./local_data.csv")

# Async execution
task_id = train_model.spawn("s3://bucket/data")
```

### Zero-Import Invocation

Execute functions without Flow imports in user code:

```python
# train.py - no Flow imports
def train_model(data_path: str, epochs: int = 100):
    import torch
    # Training logic
    return {"accuracy": 0.95}

# Infrastructure code
from flow import invoke

result = invoke(
    "train.py",
    "train_model",
    args=["s3://bucket/data"],
    kwargs={"epochs": 200},
    gpu="a100"
)
```

### Code Upload

Flow automatically uploads local code by default:

```python
# Your train.py is automatically uploaded
task = flow.run("python train.py", instance_type="a100")

# Control behavior
task = flow.run("python train.py", upload_code=False)

# Use .flowignore to exclude files (same syntax as .gitignore)
```

## Volume Management

```python
# Create persistent storage
volume = flow.create_volume(size_gb=100, name="checkpoints")

# List volumes
volumes = flow.list_volumes()
for vol in volumes:
    print(f"{vol.name}: {vol.size_gb}GB in {vol.region}")

# Attach to task
config = TaskConfig(
    instance_type="a100",
    volumes=[VolumeSpec(volume_id=volume.volume_id, mount_path="/checkpoints")]
)

# Delete volume
flow.delete_volume(volume.volume_id)
```

## Provider Architecture

### IProvider Protocol (SPI)

Clean interface for cloud provider implementations:

```python
class IProvider(Protocol):
    # Instance discovery
    def find_instances(requirements: Dict[str, Any], limit: int) -> List[Instance]
    
    # Task lifecycle
    def submit_task(instance_type: str, config: TaskConfig) -> Task
    def get_task(task_id: str) -> Task
    def stop_task(task_id: str) -> bool
    
    # Monitoring
    def get_task_logs(task_id: str, tail: int) -> str
    def stream_task_logs(task_id: str) -> Iterator[str]
    
    # Storage
    def create_volume(size_gb: int, name: str) -> Volume
    def delete_volume(volume_id: str) -> bool
    def list_volumes(limit: int) -> List[Volume]
```

### Provider Selection

```python
# Automatic based on API key
flow = Flow()  # "mithril-..." key → MithrilProvider

# Explicit provider
from flow.providers.mithril import MithrilProvider
provider = MithrilProvider(api_key="...", project="...")
flow = Flow(provider=provider)
```

## Frontend Adapters

### YAML Configuration

```yaml
name: distributed-training
instance_type: 8xa100
command: |
  torchrun --nproc_per_node=8 train.py \
    --batch-size 256 \
    --epochs 100
volumes:
  - name: datasets
    size_gb: 500
max_price_per_hour: 100.0
env:
  WANDB_API_KEY: "..."
```

### SLURM Compatibility

```bash
#!/bin/bash
#SBATCH --job-name=training
#SBATCH --gres=gpu:8

# Existing SLURM scripts work
flow slurm submit job.sbatch
```

## Data Handling

### Mount Specifications

```python
# S3 data
config = TaskConfig(
    data_mounts=[
        MountSpec(source="s3://bucket/data", target="/data")
    ]
)

# Multiple sources
config = TaskConfig(
    data_mounts=[
        MountSpec(source="s3://bucket/train", target="/train"),
        MountSpec(source="s3://bucket/val", target="/val")
    ]
)
```

### Volume Mounting

```python
# Volumes automatically mount at /volumes/<name>
volumes=[
    VolumeSpec(name="data", size_gb=100),      # → /volumes/data
    VolumeSpec(name="models", size_gb=50)      # → /volumes/models
]

# Custom mount paths
volumes=[
    VolumeSpec(name="data", mount_path="/dataset", size_gb=100)
]
```

## Error Handling

### Exception Hierarchy

```
FlowError (base)
├── AuthenticationError      # API key issues
├── ResourceNotFoundError    # Missing resources
│   └── TaskNotFoundError    # Task not found
├── ValidationError          # Invalid configuration
├── APIError                 # API communication
│   └── ValidationAPIError   # 422 errors
├── NetworkError            # Connection issues
├── TimeoutError            # Operation timeout
├── ProviderError           # Provider failures
├── ResourceNotAvailableError # No instances
├── QuotaExceededError      # Limit reached
├── VolumeError             # Storage issues
└── TaskExecutionError      # Runtime failures
```

### Structured Errors

```python
try:
    task = flow.run(config)
except ResourceNotAvailableError as e:
    print(f"Error: {e.message}")
    print("Suggestions:")
    for suggestion in e.suggestions:
        print(f"  - {suggestion}")
    print(f"Error code: {e.error_code}")
```

## Implementation Status

### Fully Implemented ✅
- Core Flow API (run, status, cancel, logs)
- TaskConfig model with validation
- Task lifecycle management
- Mithril provider implementation
- Instance type aliasing ("a100" → full spec)
- Volume management
- SSH access to instances
- Real-time log streaming
- YAML frontend adapter
- SLURM compatibility layer
- Decorator pattern (@app.function)
- Zero-import invocation
- Code upload with .flowignore
- Multi-node support
- Comprehensive error handling

### In Development 🚧
- AWS provider
- GCP provider
- Submitit frontend adapter
- Advanced scheduling constraints

### Planned ❌
- Azure provider
- Lambda Labs provider
- Kubernetes operator
- Workflow orchestration (DAGs)
- Cross-region data replication
- Spot instance bidding strategies

## Design Principles

1. **Simple tasks simple**: `flow.run("python train.py", instance_type="a100")`
2. **Complex tasks possible**: Full control via TaskConfig when needed
3. **Fail fast, explain clearly**: Validation at config time with actionable errors
4. **Provider abstraction**: Users think in tasks, not cloud-specific details
5. **Progressive disclosure**: Advanced features available but not required
6. **Type safety**: Pydantic models with comprehensive validation
7. **Zero magic**: All behavior explicit and predictable