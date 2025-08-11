# SLURM Migration Guide

Flow SDK provides a modern cloud-native alternative to SLURM while maintaining compatibility with existing workflows. This guide helps SLURM users transition to Flow.

## Command Equivalents

| SLURM Command | Flow Command | Description |
|---------------|--------------|-------------|
| `sbatch job.sh` | `flow run job.yaml` | Submit batch job |
| `sbatch script.slurm` | `flow run script.slurm` | Direct SLURM script support |
| `squeue` | `flow status` | View job queue |
| `scancel <job_id>` | `flow cancel <task_id>` | Cancel job |
| `scancel -n <name_pattern>` | `flow cancel -n <pattern>` | Cancel by name pattern |
| `scontrol show job <id>` | `flow info <task_id>` | Show job details |
| `sacct` | *Not applicable* | Flow tracks costs differently |
| `sinfo` | *Not applicable* | Cloud resources are dynamic |
| `srun` | `flow dev -c` or `flow ssh` | Interactive access |

## Log Access

```bash
# SLURM: View output files
cat slurm-12345.out

# Flow: Stream logs directly
flow logs task-abc123
flow logs task-abc123 --follow    # Like tail -f
flow logs task-abc123 --stderr     # Error output
```

## SLURM Script Compatibility

Flow can directly run existing SLURM scripts:

```bash
# Your existing SLURM script
flow run job.slurm

# Behind the scenes, Flow parses #SBATCH directives:
#SBATCH --job-name=training
#SBATCH --nodes=2
#SBATCH --gpus=a100:4
#SBATCH --time=24:00:00
#SBATCH --mem=64G
```

## Migration Examples

### Interactive Development (srun replacement)

**SLURM:**
```bash
# Interactive GPU session
srun --pty --gpus=1 --time=4:00:00 bash
srun --gpus=1 python train.py
```

**Flow (using flow dev):**
```bash
# Start persistent dev environment
flow dev  # Defaults to 8xh100
flow dev -i a100  # Or specify A100

# Run commands in containers (like srun)
flow dev -c 'python train.py'
flow dev -c bash  # Interactive shell
```

### Basic GPU Job

**SLURM:**
```bash
#!/bin/bash
#SBATCH --job-name=train-model
#SBATCH --partition=gpu
#SBATCH --gpus=1
#SBATCH --time=12:00:00
#SBATCH --mem=32G

module load cuda/11.8
python train.py
```

**Flow (YAML):**
```yaml
name: train-model
instance_type: a100
command: python train.py
max_run_time_hours: 12.0
```

**Flow (Python):**
```python
flow.run("python train.py", instance_type="a100", max_run_time_hours=12)
```

### Multi-GPU Training

**SLURM:**
```bash
#!/bin/bash
#SBATCH --job-name=distributed
#SBATCH --nodes=4
#SBATCH --gpus-per-node=8
#SBATCH --ntasks-per-node=8

srun python -m torch.distributed.launch train.py
```

**Flow:**
```yaml
name: distributed
instance_type: 8xa100
num_instances: 4
command: |
  torchrun --nproc_per_node=8 --nnodes=4 \
    --node_rank=$FLOW_NODE_RANK \
    --master_addr=$FLOW_MAIN_IP \
    train.py
```

### Array Jobs

**SLURM:**
```bash
#!/bin/bash
#SBATCH --array=1-10
#SBATCH --job-name=sweep

python experiment.py --task-id $SLURM_ARRAY_TASK_ID
```

**Flow (using loop):**
```python
for i in range(1, 11):
    flow.run(f"python experiment.py --task-id {i}", 
             name=f"sweep-{i}", instance_type="a100")
```

## Key Differences

1. **Resource Allocation**: Flow uses instance types (e.g., `a100`, `4xa100`) instead of partition/node specifications
2. **Cost Control**: Built-in `max_price_per_hour` instead of account-based billing
3. **Storage**: Cloud volumes (block storage) instead of shared filesystems
   - Mithril platform supports both block storage and file shares
   - Flow SDK currently only creates block storage volumes (requires mounting/formatting)
   - File share support is planned for easier multi-node access
4. **Environment**: Container-based instead of module system
5. **Scheduling**: Cloud-native provisioning instead of queue-based scheduling

## Environment Variables

When using the SLURM adapter (`flow run script.slurm`), Flow sets SLURM-compatible environment variables:

| SLURM Variable | Set By SLURM Adapter | Flow Native Variable |
|----------------|---------------------|---------------------|
| `SLURM_JOB_ID` | ✓ (maps to `$FLOW_TASK_ID`) | `FLOW_TASK_ID` |
| `SLURM_JOB_NAME` | ✓ | `FLOW_TASK_NAME` |
| `SLURM_ARRAY_TASK_ID` | ✓ (planned) | - |
| `SLURM_NTASKS` | ✓ | - |
| `SLURM_CPUS_PER_TASK` | ✓ | - |
| `SLURM_NNODES` | ✓ | `FLOW_NODE_COUNT` |
| `SLURM_JOB_PARTITION` | ✓ (if set) | - |

For all Flow tasks (regardless of adapter), these variables are available:
- `FLOW_TASK_ID` - Unique task identifier
- `FLOW_TASK_NAME` - Task name from config

## Advanced Features

**Module System → Container Images:**
```yaml
# SLURM: module load pytorch/2.0
# Flow equivalent:
image: pytorch/pytorch:2.0.0-cuda11.8-cudnn8
```

**Dependency Management:**
```bash
# SLURM: --dependency=afterok:12345
# Flow: Use task.wait() in Python or chain commands
```

**Output Formatting:**
```bash
# Get SLURM-style output (coming soon)
flow status --format=slurm
```

## Future Compatibility

We're considering adding direct SLURM command aliases for easier migration:
- `flow sbatch` → `flow run`
- `flow squeue` → `flow status`
- `flow scancel` → `flow cancel`

If you need specific SLURM features, please [open an issue](https://github.com/mithrilcompute/flow/issues).