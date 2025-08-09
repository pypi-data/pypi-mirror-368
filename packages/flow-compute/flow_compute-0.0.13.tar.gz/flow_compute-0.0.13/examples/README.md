# Flow SDK Examples

A curated collection of examples demonstrating Flow SDK capabilities, organized by complexity and use case.

## Prerequisites

- Flow SDK installed (`uv add flow-sdk`)
- Valid API key configured (`flow init`)
- Python 3.8 or later

## Quick Start

New to Flow? Start here:
```bash
python 01_basics/hello_gpu.py
```

## Example Organization

### 01_basics/ - Getting Started
Learn the fundamentals of submitting and managing GPU jobs.

- `hello_gpu.py` - Your first GPU job
- `instance_types.py` - Explore available GPU instances
- `task_lifecycle.py` - Submit, monitor, and manage tasks

### 02_storage/ - Data and Storage
Work with persistent volumes and cloud storage.

- `data_pipeline.py` - S3/GCS data workflows
- More examples coming soon: persistent volumes, checkpointing

### 03_development/ - Interactive Development
Tools for development and debugging.

- `jupyter_server.py` - Launch Jupyter on GPU instances
- `local_testing.py` - Test workflows locally before cloud deployment

### 04_distributed/ - Scaling Up
Multi-GPU and multi-node workflows.

- `multi_node.py` - Distributed training across multiple nodes
- More examples coming soon: single-node multi-GPU, parameter sweeps

### 05_production/ - Production Patterns
Best practices for production deployments.

- `logging_patterns.py` - Advanced logging and monitoring
- More examples coming soon: fault tolerance, cost optimization

### configs/ - Configuration Examples
YAML configuration files demonstrating various setups.

- `basic.yaml` - Minimal configuration
- `gpu_instance.yaml` - GPU with storage
- `multi_node.yaml` - Distributed setup
- `single_node_multi_gpu.yaml` - Multi-GPU single node
- `full_example.yaml` - Complete reference

### notebooks/ - Interactive Tutorials
Jupyter notebooks for learning and experimentation.

- `2_configuration_auth.ipynb` - Configuration and authentication
- `3_frontends_comparison.ipynb` - Different submission methods
- `4_advanced_features.ipynb` - Advanced capabilities
- `5_real_world_examples.ipynb` - Production workflows

## Learning Path

1. **Start**: Run `hello_gpu.py` to verify your setup
2. **Explore**: Use `instance_types.py` to find available GPUs
3. **Develop**: Launch `jupyter_server.py` for interactive development
4. **Scale**: Try `multi_node.py` for distributed workloads
5. **Deploy**: Apply patterns from `05_production/` for production use

## Running Examples

All examples are self-contained and can be run directly:

```bash
python examples/01_basics/hello_gpu.py
```

## Testing Examples

To verify all examples are working correctly:
```bash
pytest tests/test_examples.py
```

## Contributing

When adding new examples:
1. Place in the appropriate category directory
2. Use clear, action-based naming
3. Include docstring explaining what the example demonstrates
4. Keep examples focused on a single concept
5. Add any required dependencies to the docstring