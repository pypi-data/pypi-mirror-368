# SLURM Adapter Demo

This demonstrates the Flow SDK's SLURM compatibility layer, which allows running existing SLURM batch scripts.

## Created Examples

### 1. Basic GPU Test (`gpu_test_slurm.sh`)
- Single node with 8x H100 GPUs
- Basic GPU verification and system checks
- 30-minute runtime limit

### 2. Distributed Training (`gpu_training_slurm.sh`)
- Multi-node setup (2 nodes)
- Array job with 3 tasks (different learning rates)
- 4x A100 GPUs per node
- Environment variable export
- Module loading (CUDA, Python, OpenMPI)

## Test Results

The SLURM adapter successfully:

1. **Parses SLURM directives** - Correctly extracts job name, partition, resources
2. **Maps GPU specifications** - Converts `--gpus=h100:8` to Flow instance types
3. **Handles array jobs** - Creates multiple task configs for array indices
4. **Preserves environment** - Exports variables and SLURM compatibility vars
5. **Maintains script content** - Module loads and commands are preserved
6. **Supports overrides** - CLI options can override script directives

## Key Features Demonstrated

- Job arrays (`--array=1-3`)
- Multi-node jobs (`--nodes=2`)
- GPU specification (`--gpus=a100:4`)
- Memory limits (`--mem=256G`)
- Time limits (`--time=12:00:00`)
- Environment export (`--export=VAR=value`)
- Output redirection (`--output`, `--error`)
- Module loading preservation

## Usage

```bash
# Direct execution (when implemented in CLI)
flow run --slurm gpu_test_slurm.sh

# Programmatic usage
from flow._internal.frontends.slurm.adapter import SlurmFrontendAdapter
from flow import Flow

adapter = SlurmFrontendAdapter()
task_config = await adapter.parse_and_convert("script.sh")
with Flow() as flow:
    task = flow.run(task_config)
```

## Notes

- The "Unknown partition 'gpu'" warning is expected - partitions can be mapped via configuration
- SLURM environment variables are automatically set for compatibility
- Array jobs create separate Flow tasks with appropriate SLURM_ARRAY_TASK_ID values