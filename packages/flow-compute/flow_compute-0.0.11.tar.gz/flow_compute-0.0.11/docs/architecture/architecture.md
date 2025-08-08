# Architecture

## Overview

Flow SDK is a comprehensive platform for GPU compute orchestration, providing both high-level abstractions for ML/AI workloads and low-level control for infrastructure management. The architecture consists of two main components:

1. **Flow SDK**: High-level Python SDK with automatic resource management
2. **Mithril CLI**: Low-level infrastructure control following Unix philosophy

## Core Design Principles

1. **Simple by default**: One line to run on GPU
2. **Progressive disclosure**: Complexity available when needed
3. **Provider agnostic**: Clean abstractions over cloud specifics
4. **Fail fast**: Validate early with clear errors
5. **Zero magic**: Explicit behavior, predictable types

## System Components

```
┌──────────────────────────────────────────────────────────────┐
│                         User Layer                           │
│  ┌─────────────────────┐        ┌──────────────────────┐     │
│  │   Python Scripts    │        │   CLI Commands       │     │
│  │  flow.run(...)      │        │  flow run ...        │     │
│  └──────────┬──────────┘        └───────────┬──────────┘     │
└─────────────┼────────────────────────────────┼───────────────┘
              │                                │
┌─────────────▼────────────────────────────────▼───────────────┐
│                      Flow SDK Core                           │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   High-Level   │  │   Instance   │  │   Provider   │      │
│  │      API       │  │   Catalog    │  │  Interface   │      │
│  └────────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
              │
┌─────────────▼────────────────────────────────────────────────┐
│                    Provider Layer                            │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │      Mithril       │  │    Local     │  │   Future     │      │
│  │   Provider     │  │  Provider    │  │  Providers   │      │
│  └────────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
              │
┌─────────────▼────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Cloud APIs    │  │   Docker     │  │  AWS/GCP/    │      │
│  │  (Mithril, etc)    │  │  Containers  │  │    Azure     │      │
│  └────────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

## Component Details

### User API Layer

#### Flow Class (`flow.py`)
Primary interface for task submission and management.

```python
class Flow:
    def run(command_or_config, **kwargs) -> Task
    def run(command, gpu="a100", **kwargs) -> Task
    def invoke(module, function, *args, **kwargs) -> Any
    def get_task(task_id: str) -> Task
    def list_tasks(limit: int = 100) -> List[Task]
    def find_instances(requirements: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]
```

**Key responsibilities:**
- Provider initialization and selection
- Configuration validation
- Task submission and lifecycle management
- Resource discovery

#### TaskConfig (`models.py`)
Strongly-typed configuration model with comprehensive validation.

```python
class TaskConfig:
    # Identification
    name: str
    
    # Instance specification (exactly ONE required)
    instance_type: Optional[str]      # "a100", "8xh100"
    min_gpu_memory_gb: Optional[int]  # Capability-based
    
    # Command specification (exactly ONE required)
    command: Optional[List[str]]      # ["python", "train.py"]
    shell: Optional[str]              # Shell command string
    script: Optional[str]             # Script content
    
    # Resources
    volumes: List[VolumeSpec]
    env: Dict[str, str]
    data: Dict[str, str]              # Data mounts
    
    # Limits
    max_price_per_hour: Optional[float]
    max_run_time_hours: Optional[float]
```

#### Task (`models.py`)
Handle for running/completed tasks with rich functionality.

```python
class Task:
    task_id: str
    status: str  # "pending", "running", "completed", "failed"
    instance_type: str
    
    def logs(follow: bool = False) -> Union[str, Iterator[str]]
    def cancel() -> None
    def wait(timeout: int = None) -> None
    def ssh(command: Optional[str] = None) -> None
    def get_instances() -> List[Instance]
    def get_user() -> User
```

### Frontend Adapters

Multiple input formats converging to unified TaskConfig:

#### YAML Frontend
```yaml
name: training
instance_type: a100
command: python train.py
volumes:
  - name: data
    size_gb: 100
data:
  /datasets: s3://my-bucket/data
```

#### SLURM Frontend
Converts SLURM scripts to TaskConfig:
```bash
#!/bin/bash
#SBATCH --gres=gpu:8
#SBATCH --mem=32G
#SBATCH --time=24:00:00

python train.py
```

#### CLI Frontend
Command-line interface:
```bash
flow run "python train.py" --instance-type a100
flow run training.yaml
flow status
flow logs task-abc123
```

### Core Domain

#### Instance Resolution
Flexible instance type specification with smart resolution:

```python
# User input → Canonical form → Provider ID
"a100"     → "a100-80gb.sxm.1x" → "it_MsIRhxj3ccyVWGfP"
"4xa100"   → "a100-80gb.sxm.4x" → "it_fK7Cx6TVhOK5ZfXT"
"8xh100"   → "h100-80gb.sxm.8x" → "it_5ECSoHQjLBzrp5YM"

# Capability-based selection
min_gpu_memory_gb=80 → Best available GPU with 80GB+ VRAM
```

#### Catalog System
Dynamic instance discovery and capability matching:

```python
# Search by requirements
instances = flow.find_instances({
    "gpu_memory_gb": 40,
    "max_price": 10.0,
    "region": "us-west-2"
})
```

#### Task Lifecycle
Managed state transitions with automatic error handling:

```
pending → provisioning → running → completed
               ↓            ↓
            failed      cancelled
```

### Provider Interface

Clean abstraction enabling multi-cloud support:

```python
class IProvider(Protocol):
    def submit_task(config: TaskConfig) -> str
    def get_task(task_id: str) -> TaskStatus
    def cancel_task(task_id: str) -> bool
    def get_logs(task_id: str, follow: bool) -> Iterator[str]
    def list_available_instances() -> List[InstanceType]
```

### Provider Implementations

#### Mithril Provider (Production)
- **Spot auction system**: Automatic bidding for best prices
- **Startup script generation**: Cloud-init compatible
- **Volume management**: Block storage with file shares coming soon
- **Multi-region support**: Automatic region selection

#### Local Provider (Development)
- **Docker-based**: Container isolation for testing
- **Mock GPU**: Development without hardware
- **File volumes**: Direct filesystem mounting
- **Process logs**: Real-time output capture

## Key Design Patterns

### 1. Strategy Pattern for Providers
```python
# Automatic provider selection based on configuration
provider = ProviderFactory.get_provider(api_endpoint)
task_id = provider.submit_task(config)
```

### 2. Builder Pattern for Complex Objects
```python
# Fluent interface for configuration
config = TaskConfig.builder()
    .with_gpu("a100")
    .with_command("python train.py")
    .with_volume("data", size_gb=100)
    .with_env("WANDB_KEY", "...")
    .build()
```

### 3. Progressive Disclosure
```python
# Simple: One line
flow.run("python train.py", gpu="a100")

# Advanced: Full control
config = TaskConfig(
    instance_type="a100-80gb.sxm.4x",
    command=["python", "-m", "torch.distributed.launch", "train.py"],
    volumes=[VolumeSpec(name="models", size_gb=500)],
    max_price_per_hour=15.0
)
```

## Data Flow Examples

### Task Submission Flow
```
1. User: flow.run("python train.py", gpu="a100")
2. SDK: Validate configuration
3. SDK: Resolve instance type (a100 → canonical → FID)
4. SDK: Select provider (Mithril)
5. Provider: Submit spot bid
6. Provider: Generate startup script
7. Cloud: Provision instance
8. Cloud: Execute startup script
9. SDK: Return Task handle
10. User: Monitor via task.logs()
```

### Data Mounting Flow
```
1. User: flow.submit(command, data={"/data": "s3://bucket/path"})
2. SDK: Parse data specification
3. SDK: Inject AWS credentials
4. Provider: Add s3fs mount to startup script
5. Instance: Mount S3 bucket at /data
6. Task: Access data as local filesystem
```

## Configuration Hierarchy

Configuration follows a clear precedence order:

```
1. Command arguments (highest priority)
2. Environment variables (Mithril_API_KEY, etc.)
3. Configuration files (~/.flow/config.yaml)
4. Project settings (flow.yaml)
5. Defaults (lowest priority)
```

## Error Handling Philosophy

### Validation Errors
Early validation with helpful suggestions:
```python
ValidationError: Invalid instance type 'a100x8'
  Did you mean: '8xa100'?
  Valid formats: 'a100', '2xa100', '4xa100', '8xa100'
```

### Resource Errors
Clear guidance on resolution:
```python
InsufficientQuotaError: Quota exceeded in us-east-1
  Current quota: 4 A100 GPUs
  Requested: 8 A100 GPUs
  Suggestions:
    - Try region: us-west-2
    - Contact support for quota increase
```

### Transient Errors
Automatic retry with exponential backoff:
- API rate limits
- Network timeouts
- Spot instance outbid

## Security Architecture

### Authentication
- **API keys**: Stored securely in environment/config
- **SSH keys**: Separate key management system
- **No hardcoded secrets**: All credentials external

### Network Security
- **HTTPS only**: All API communication encrypted
- **SSH access**: Key-based authentication only
- **VPC isolation**: Project-scoped networks

### Data Protection
- **Encrypted volumes**: At-rest encryption
- **Secure injection**: Environment variables for secrets
- **Temporary URLs**: Time-limited S3 access

## Performance Characteristics

### Startup Times
- **Cold start**: 2-3 minutes (instance provisioning)
- **Warm start**: 30-60 seconds (pre-allocated pool)
- **Container ready**: Additional 10-30 seconds

### Resource Limits
- **Startup script**: 10KB limit (compressed if larger)
- **Environment variables**: 4KB total
- **Concurrent tasks**: 100 per project
- **API rate limit**: 100 requests/minute

### Network Performance
- **Inter-node**: 100 Gbps bandwidth
- **Storage**: 3 GB/s NVMe throughput
- **S3 bandwidth**: 10 Gbps per instance

## Extension Points

### Adding a New Provider

1. Implement the `IProvider` protocol
2. Add provider-specific configuration
3. Register in provider factory
4. Map instance types

Example:
```python
class AWSProvider:
    def submit_task(self, config: TaskConfig) -> str:
        # Convert to AWS Batch job
        # Submit to AWS API
        # Return job ID
```

### Adding Instance Types

1. Update parser patterns in `resources/parser.py`
2. Add to instance catalog
3. Map to provider-specific IDs
4. Update documentation

### Custom Frontends

Create adapters for new input formats:
```python
class KubernetesAdapter:
    def parse_job_spec(yaml: str) -> TaskConfig:
        # Convert K8s Job to TaskConfig
```

## Best Practices

### For Users

1. **Start simple**: Use `flow.run()` with minimal options
2. **Use capability selection**: Let SDK choose instance types
3. **Set cost limits**: Always use `max_price_per_hour`
4. **Monitor logs**: Use `flow logs -f` for real-time updates
5. **Clean up resources**: Volumes persist after tasks

### For Contributors

1. **Follow patterns**: Use existing patterns for consistency
2. **Add tests**: Unit, integration, and contract tests
3. **Document changes**: Update both code and user docs
4. **Consider compatibility**: Maintain backward compatibility
5. **Security first**: Never log sensitive information

## Future Roadmap

### Near Term
- **Multi-cloud support**: AWS, GCP, Azure providers
- **Workflow DAGs**: Task dependencies and pipelines
- **Result caching**: Automatic output memoization
- **Cost optimization**: Smart instance selection

### Long Term
- **Federation**: Cross-region/account orchestration
- **Edge computing**: Support for edge GPUs
- **Serverless GPU**: Function-as-a-service model
- **ML-specific features**: Dataset versioning, experiment tracking

## Summary

Flow SDK's architecture achieves simplicity through careful layering:

- **Simple user API** hides infrastructure complexity
- **Clean abstractions** enable multi-cloud extensibility  
- **Strong typing** catches errors early with helpful messages
- **Provider pattern** supports current and future clouds

The design prioritizes developer experience while maintaining the flexibility to evolve with changing cloud landscapes and user needs.