# Architecture Overview

Flow SDK provides a unified interface for GPU workloads across cloud providers.

## Core Concepts

**Tasks**: Units of work executed on GPU infrastructure
- Commands: `python train.py`
- Distributed jobs: Multi-node training
- Services: Model servers

**Providers**: Cloud platform handlers
- Mithril 
- Local (development)
- AWS, GCP, Azure (planned)

**Volumes**: Persistent storage
- Survives task completion
- Shared across tasks
- Independent of compute

## System Layers

1. **User Interface Layer**
   - Python API: `flow.run()`, `flow.submit()`, `flow.invoke()`
   - CLI: `flow run`, `flow status`, `flow logs`
   - YAML: Configuration files

2. **Core Domain Layer**
   - TaskConfig: Configuration validation
   - Task: Execution state
   - Volume: Storage management

3. **Provider Abstraction**
   - IProvider protocol
   - Submit, monitor, stream, manage

4. **Provider Implementations**
   - Cloud-specific adapters
   - Authentication handling
   - Lifecycle management

## Design Principles

### Progressive Disclosure

Simple:
```python
flow.run("python train.py", gpu="a100")
```

Complex:
```python
config = TaskConfig(
    name="distributed-training",
    instance_type="8xa100",
    num_instances=4,
    volumes=[...],
    env={...}
)
```

### Fail-Fast Validation
- Early configuration checks
- Quota verification
- Resource availability

### Cloud Agnostic
- Portable code
- Optional provider features
- Easy migration

## Execution Flow

### Submission
1. User submits via API/CLI
2. Configuration validated
3. Provider translates format
4. Resources provisioned
5. Task ID returned

### Execution
1. Instance boots runtime
2. Environment configured
3. Command executes
4. Logs stream
5. Results persist

### Completion
1. Exit code captured
2. Logs finalized
3. Instance terminated
4. Volumes preserved

## Security

**Authentication**
- Secure API keys
- Provider credentials
- No logged secrets

**Network**
- HTTPS APIs
- SSH keys
- Isolated VPCs

**Data**
- Encrypted volumes
- Secure injection
- Clean logs

## Performance

**Startup**
- Cold: 2-3 minutes
- Warm: 30-60 seconds
- Container: Size-dependent

**Network**
- API: <200ms latency
- Logs: 50-100ms chunks
- Inter-node: 100 Gbps

**Storage**
- IOPS: 16,000
- Throughput: 1 GB/s
- Latency: <1ms

## Extensibility

**Providers**: Implement IProvider interface
- Authentication
- Instance management
- Log streaming
- Volume operations

**Frontends**: Alternative interfaces
- Kubernetes adapters
- SLURM compatibility
- Notebook integration

**Plugins**: Planned extensions
- Custom resources
- Workflow engines
- Result stores