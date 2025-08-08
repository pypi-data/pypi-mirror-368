# API Reference

## Core Classes

### Flow

The main interface for submitting and managing GPU workloads.

```python
from flow import Flow

flow = Flow(api_key: Optional[str] = None)
```

#### Parameters

- `api_key` (str, optional): Mithril API key. If not provided, uses environment variable or prompts.

#### Methods

##### `run(command_or_config, **kwargs) -> Task`

Submit a task to run on GPU infrastructure.

**Parameters:**
- `command_or_config`: Either a command string or TaskConfig object
- `**kwargs`: If command is a string, these override TaskConfig defaults:
  - `instance_type` (str): GPU instance type (e.g., "a100", "8xh100")
  - `name` (str): Task name for identification
  - `volumes` (List[Dict]): Persistent storage volumes
  - `env` (Dict[str, str]): Environment variables
  - `max_price_per_hour` (float): Maximum spot price
  - `max_run_time_hours` (float, optional): Maximum runtime before termination
  - `num_instances` (int): Number of nodes for distributed training
  - `image` (str): Docker image (default: "ubuntu:22.04")
  - `ports` (List[int]): Ports to expose

**Returns:** `Task` object for monitoring and control

**Examples:**
```python
# Simple command
task = flow.run("python train.py", instance_type="a100")

# With configuration
task = flow.run(
    "python train.py",
    instance_type="4xa100",
    volumes=[{"name": "data", "size_gb": 100}],
    max_price_per_hour=10.0
)

# Using TaskConfig
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    volumes=[VolumeSpec(name="data", size_gb=100)]
)
task = flow.run(config)
```

##### `find_instances(requirements: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]`

Find available GPU instances matching requirements.

**Parameters:**
- `requirements` (Dict[str, Any]): Constraint dictionary with optional keys:
  - `instance_type` (str): Exact instance type (e.g., "a100", "8xh100")
  - `min_gpu_count` (int): Minimum number of GPUs (1-64)
  - `max_price` (float): Maximum hourly price in USD
  - `region` (str): Target region/zone
  - `gpu_memory_gb` (int): Minimum GPU memory per device (16, 24, 40, 80)
  - `gpu_type` (str): GPU model ("a100", "v100", "h100")
- `limit` (int): Maximum results to return (1-100)

**Returns:** List of available instances sorted by price

**Example:**
```python
# Find cheapest GPU with 80GB+ memory
instances = flow.find_instances({"gpu_memory_gb": 80})
for inst in instances[:5]:
    print(f"{inst['instance_type']}: ${inst['price_per_hour']}/hr")
```

##### `list_tasks(limit: int = 100) -> List[Task]`

List recent tasks.

**Returns:** List of Task objects

##### `get_task(task_id: str) -> Task`

Get a specific task by ID.

**Returns:** Task object

##### `create_volume(size_gb: int, name: Optional[str] = None, interface: str = "block") -> Volume`

Create a persistent storage volume.

**Parameters:**
- `size_gb` (int): Volume size in gigabytes
- `name` (str, optional): Human-readable name for the volume
- `interface` (str): Storage type - "block" or "file" (default: "block")

**Returns:** Volume object with id, name, and metadata

**Example:**
```python
volume = flow.create_volume(100, "training-data")
```

##### `delete_volume(volume_id: str) -> None`

Delete a storage volume.

**Parameters:**
- `volume_id` (str): Volume ID or name to delete

**Raises:** FlowError if deletion fails (e.g., volume attached to running task)

##### `list_volumes(limit: int = 100) -> List[Volume]`

List all volumes in the current project.

**Parameters:**
- `limit` (int): Maximum volumes to return (default: 100)

**Returns:** List of Volume objects

##### `mount_volume(volume_id: str, task_id: str) -> None`

Mount a volume to a running task without restart.

**Parameters:**
- `volume_id` (str): Volume ID or name to mount
- `task_id` (str): Task ID to mount the volume to

**Raises:**
- `ResourceNotFoundError`: Task or volume not found
- `ValidationError`: Region mismatch or volume already attached
- `FlowError`: Mount operation failed

**Example:**
```python
# Create and mount volume to running task
volume = flow.create_volume(100, "shared-data")
task = flow.run("python server.py", instance_type="a100")
flow.mount_volume("shared-data", task.task_id)
# Volume now available at /mnt/shared-data
```

### Task

Task objects are returned by `flow.run()` and provide complete interaction with running or completed tasks. They encapsulate all information and functionality needed to monitor, access, and control task execution.

#### Attributes

```python
class Task:
    # Identification
    task_id: str                    # Unique task identifier
    name: str                       # Task name from config
    
    # Status
    status: TaskStatus              # Current status (enum)
    message: Optional[str]          # Status message or error details
    
    # Timestamps  
    created_at: datetime            # When task was created
    started_at: Optional[datetime]  # When execution started
    completed_at: Optional[datetime] # When execution finished
    
    # Resources
    instance_type: str              # Instance type (e.g., "a100", "8xh100")
    num_instances: int              # Number of instances
    region: str                     # Deployment region
    instances: List[str]            # Instance IDs
    
    # Cost tracking
    cost_per_hour: str              # Hourly cost (e.g., "$25.60")
    total_cost: Optional[str]       # Total accumulated cost
    
    # SSH access
    ssh_host: Optional[str]         # SSH hostname/IP (when running)
    ssh_port: int = 22              # SSH port
    ssh_user: str = "ubuntu"        # SSH username  
    ssh_command: Optional[str]      # Complete SSH command string
    
    # Service endpoints
    endpoints: Dict[str, str]       # Service URLs (e.g., Jupyter)
    
    # Configuration
    config: Optional[TaskConfig]    # Original task configuration
```

#### Properties

```python
task.is_running    # True if status == RUNNING
task.is_terminal   # True if in terminal state (completed/failed/cancelled)
```

#### Methods

##### `logs(follow: bool = False, tail: int = 100) -> Union[str, Iterator[str]]`

Retrieve task output logs.

**Parameters:**
- `follow` (bool): Stream logs in real-time (returns iterator)
- `tail` (int): Number of recent lines to return (default: 100)

**Returns:** 
- If `follow=False`: String containing logs
- If `follow=True`: Iterator yielding log lines

**Example:**
```python
# Get recent logs
print(task.logs())

# Get last 1000 lines
print(task.logs(tail=1000))

# Stream logs in real-time
for line in task.logs(follow=True):
    print(line.rstrip())
```

##### `wait(timeout: Optional[int] = None) -> None`

Block until task reaches terminal state.

**Parameters:**
- `timeout` (int): Maximum seconds to wait (raises TimeoutError if exceeded)

**Example:**
```python
# Wait indefinitely
task.wait()

# Wait up to 5 minutes
task.wait(timeout=300)
```

##### `refresh() -> None`

Update task information from provider.

```python
task.refresh()
print(f"Updated status: {task.status}")
```

##### `stop() -> None` / `cancel() -> None`

Terminate the running task. Both methods are equivalent.

```python
task.stop()  # or task.cancel()
```

##### `shell(command: Optional[str] = None, node: Optional[int] = None) -> None`

Open shell session or execute remote command.

**Parameters:**
- `command` (str): Command to execute remotely (if None, opens interactive session)
- `node` (int): For multi-node tasks, which node to connect to (0-based)

**Example:**
```python
# Interactive shell session
task.shell()

# Execute command
task.shell(command="nvidia-smi")

# Connect to specific node
task.shell(node=1)  # Connect to second node
```

### TaskConfig

Configuration for GPU workloads using Pydantic validation.

```python
from flow.models import TaskConfig

config = TaskConfig(
    name: str,                           # Required: alphanumeric + dash/underscore
    
    # Instance specification (exactly ONE required)
    instance_type: Optional[str] = None,         # "a100", "8xh100", etc.
    min_gpu_memory_gb: Optional[int] = None,     # Capability-based selection
    
    # Command specification (required)
    command: Union[str, List[str]],              # "python train.py" or ["python", "train.py"]
    
    # Resources
    volumes: List[VolumeSpec] = [],
    env: Dict[str, str] = {},                    # Environment variables
    ssh_keys: List[str] = [],                    # SSH key names (plural!)
    
    # Limits
    max_price_per_hour: Optional[float] = None,
    max_run_time_hours: Optional[float] = None,  # Optional, max 168 (7 days)
    
    # Multi-node
    num_instances: int = 1,                      # Number of nodes
    
    # Other
    image: str = "ubuntu:22.04",
    working_dir: str = "/workspace",
    region: Optional[str] = None,
    ports: List[int] = []
)
```

### VolumeSpec

Persistent storage configuration.

```python
from flow.models import VolumeSpec

volume = VolumeSpec(
    name: str,                    # Unique identifier
    size_gb: int = 100,          # Size in gigabytes
    mount_path: str = "/data"    # Mount location in container
)
```

## Instance Types

### Supported Formats

```python
# Simple names (recommended)
"a100"     # 1x A100 80GB
"2xa100"   # 2x A100 80GB
"4xa100"   # 4x A100 80GB
"8xa100"   # 8x A100 80GB
"h100"     # 8x H100 80GB (default)
"8xh100"   # 8x H100 80GB (explicit)

# Full Mithril format
"a100-80gb.sxm.1x"
"h100-80gb.pcie.1x"

# Direct FID (if known)
"it_MsIRhxj3ccyVWGfP"
```

### Not Supported

```python
"a100x8"          # Wrong format - use "8xa100"
"A100"            # Wrong case - use lowercase
"gpu.nvidia.a100" # No prefixes
"nvidia-a100"     # No vendor prefixes
```

## Errors

All Flow SDK errors inherit from `FlowError`.

### Common Errors

```python
from flow.errors import (
    AuthenticationError,      # Missing/invalid API key
    ValidationError,          # Invalid configuration
    ResourceNotFoundError,    # Instance type not found
    InsufficientQuotaError,   # Quota exceeded
    TaskExecutionError,       # Task failed during execution
    TimeoutError             # Operation timed out
)
```

### Error Handling

```python
from flow.errors import FlowError, ValidationError

try:
    task = flow.run("python train.py", instance_type="invalid")
except ValidationError as e:
    print(f"Configuration error: {e}")
    print(f"Suggestions: {e.suggestions}")
except FlowError as e:
    print(f"Flow error: {e}")
```

## Functions

### invoke

Execute functions remotely without modifying source code.

```python
from flow import invoke

result = invoke(
    module: str,                    # Python file path
    function: str,                  # Function name
    args: List[Any] = [],          # Positional arguments
    kwargs: Dict[str, Any] = {},   # Keyword arguments
    gpu: str = None,               # Instance type
    **config_kwargs                # Additional TaskConfig options
) -> Any
```

**Example:**
```python
# Execute train_model() from train.py on GPU
result = invoke(
    "train.py",
    "train_model",
    args=["dataset.csv"],
    kwargs={"epochs": 100},
    gpu="a100"
)
```

## Environment Variables

Flow SDK reads these environment variables:

```bash
Mithril_API_KEY          # API authentication key
Mithril_PROJECT          # Default project ID
Mithril_REGION           # Default region
Mithril_SSH_KEY          # Default SSH key name
FLOW_MAX_PRICE       # Default max price per hour
FLOW_DEBUG           # Enable debug logging
```

## Volume Management

### Creating Volumes

```python
# Via task configuration
volumes=[{"name": "my-data", "size_gb": 100}]

# Volumes persist across tasks
task1 = flow.run("python prep.py", volumes=[{"name": "data", "size_gb": 100}])
task2 = flow.run("python train.py", volumes=[{"name": "data"}])  # Reuses volume
```

### Volume Lifecycle

- Created automatically on first use
- Persist until explicitly deleted
- Accessible across tasks in same project
- Billed per GB per month

## Multi-Node Training

For distributed workloads:

```python
task = flow.run(
    "torchrun train.py",
    instance_type="8xa100",
    num_instances=4  # Creates 4-node cluster
)
```

Environment variables set automatically:
- `FLOW_NODE_RANK`: Node index (0, 1, 2, 3)
- `FLOW_NUM_NODES`: Total nodes (4)
- `FLOW_MAIN_IP`: IP address of rank 0 node

## Cost Management

### Price Limits

```python
# Set maximum hourly price
max_price_per_hour=10.0  # Uses spot when available

# Optional: set maximum runtime
# max_run_time_hours=24.0  # Force termination after 24 hours
```

### Monitoring Costs

```python
task = flow.get_task("task-abc123")
print(f"Current cost: {task.total_cost}")
print(f"Hourly rate: {task.cost_per_hour}/hr")
```

## Advanced Features

### Custom Images

```python
# Use custom Docker image
task = flow.run(
    "python train.py",
    image="nvcr.io/nvidia/pytorch:23.10-py3"
)
```

### Port Forwarding

```python
# Expose ports for services
task = flow.run(
    "jupyter lab --ip=0.0.0.0",
    ports=[8888]
)
print(f"Access at: http://{task.host}:8888")
```

### Startup Scripts

```python
# Run setup commands as part of the main command
config = TaskConfig(
    command="""bash -c '
        apt-get update && 
        apt-get install -y libgl1-mesa-glx && 
        pip install -r requirements.txt && 
        python app.py
    '"""
)
```

## Best Practices

1. **Always set price limits** to prevent unexpected costs
2. **Use volumes** for data that needs to persist
3. **Consider max_run_time_hours** as a safety net (optional)
4. **Use specific instance types** rather than capability-based selection for reproducibility
5. **Monitor task logs** to catch issues early

## Complete Example

```python
from flow import Flow, TaskConfig
from flow.models import VolumeSpec

# Initialize Flow
flow = Flow()

# Configure task
config = TaskConfig(
    name="training-run-42",
    command="python train.py --epochs 100",
    instance_type="4xa100",
    volumes=[
        VolumeSpec(name="dataset", size_gb=500, mount_path="/data"),
        VolumeSpec(name="checkpoints", size_gb=100, mount_path="/checkpoints")
    ],
    env={
        "WANDB_API_KEY": "your-key",
        "CUDA_VISIBLE_DEVICES": "0,1,2,3"
    },
    max_price_per_hour=20.0,
    # Optional time limit
    # max_run_time_hours=72.0
)

# Submit task
task = flow.run(config)
print(f"Task {task.task_id} submitted")

# Monitor progress
for line in task.logs(follow=True):
    if "loss:" in line:
        print(line)

# Wait for completion
task.wait()
print(f"Task completed with status: {task.status}")
```