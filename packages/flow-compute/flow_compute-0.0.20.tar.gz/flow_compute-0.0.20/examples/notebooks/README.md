# Flow Compute Tutorial Notebooks

This directory contains a comprehensive set of Jupyter notebooks that demonstrate the key features and capabilities of Flow SDK. The notebooks are organized in a progressive manner, from basic concepts to advanced real-world applications.

## Prerequisites

- Python 3.11 or later
- Flow Compute installed (`pip install flow-compute`)
- Jupyter installed (`pip install jupyter notebook`)
- Configured Flow credentials (`flow init`)

## Notebooks Overview

### 1. [Quickstart Basics](1_quickstart_basics.ipynb)
**Learn the fundamentals of Flow Compute**
- Installation and setup
- Basic task submission with `TaskConfig`
- Monitoring task status and logs
- Working with different instance types
- Storage volumes basics
- Error handling and debugging

**Start here if you're new to Flow Compute!**

### 2. [Configuration & Authentication](2_configuration_auth.ipynb)
**Master Flow SDK configuration**
- Understanding the configuration hierarchy
- Authentication methods and API keys
- Project-specific configurations
- SSH key management
- Environment variables
- Provider selection (Mithril, AWS, GCP, Azure)
- Security best practices

### 3. [Frontends Comparison](3_frontends_comparison.ipynb)
**Explore different ways to use Flow SDK**
- Python API - Direct programmatic interface
- YAML configurations - Declarative task definitions
- SLURM adapter - For HPC users
- CLI commands - Command-line interface
- Submitit integration - For parameter sweeps
- Choosing the right frontend for your use case

### 4. [Advanced Features](4_advanced_features.ipynb)
**Leverage advanced capabilities**
- Instance catalog and smart selection
- Persistent storage management
- Multi-node distributed computing
- Port forwarding for interactive services
- Custom startup scripts
- Self-terminating tasks for cost optimization
- Monitoring and observability

### 5. [Real-World Examples](5_real_world_examples.ipynb)
**Production-ready workflows**
- End-to-end ML pipeline (data → training → deployment)
- Distributed hyperparameter optimization
- Large model training with DeepSpeed
- Fault-tolerant data processing pipelines
- Complete ML development environment
- Auto-scaling inference service

## How to Use These Notebooks

1. **Sequential Learning Path**: Start with notebook 1 and progress through to notebook 5. Each notebook builds on concepts from previous ones.

2. **Reference Guide**: Jump to specific notebooks based on your needs:
   - New to Flow? → Start with notebook 1
   - Need to configure Flow? → See notebook 2
   - Comparing submission methods? → Check notebook 3
   - Looking for advanced patterns? → Explore notebook 4
   - Building production systems? → Study notebook 5

3. **Run Interactively**: 
   ```bash
   # Start Jupyter
   jupyter notebook
   
   # Or use Jupyter Lab
   jupyter lab
   ```

4. **Copy and Adapt**: Feel free to copy code snippets and adapt them for your use cases.

## Key Concepts Covered

- **Task Management**: Submit, monitor, and control computational tasks
- **Resource Selection**: Choose optimal instances based on workload requirements
- **Storage**: Persistent volumes for data and model storage
- **Scaling**: From single tasks to distributed multi-node workflows
- **Cost Optimization**: Price limits, spot instances, auto-termination
- **Production Patterns**: Error handling, checkpointing, monitoring

## Quick Examples

### Submit a simple GPU task
```python
from flow import Flow, TaskConfig

config = TaskConfig(
    name="gpu-task",
    instance_type="gpu.nvidia.t4",
    command="python train.py"
)

with Flow() as flow:
    task = flow.run(config, wait=True)
    print(task.logs())
```

### Find available instances
```python
with Flow() as flow:
    instances = flow.find_instances({
        "max_price": 10.0,
        "min_gpu_count": 1
    })
    for inst in instances:
        print(f"{inst.instance_type}: ${inst.price_per_hour}/hr")
```

## Tips

- **Always set price limits** to avoid unexpected costs
- **Use persistent volumes** for data that needs to survive task completion
- **Start small** - test with cheaper instances before scaling up
- **Monitor your tasks** - use logs and status checks
- **Handle failures gracefully** - implement retries and checkpoints

## Need Help?

- Check the Flow documentation
- Join the community forum for support
- Report issues on GitHub

Happy computing with Flow SDK! 🚀