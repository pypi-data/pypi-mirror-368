# SLURM to Flow Migration

Seamlessly transition from SLURM to Flow with familiar commands and workflows.

## Command Translation

### Basic Commands

| SLURM Command | Flow Equivalent | Description |
|---------------|-----------------|-------------|
| `sbatch job.sh` | `flow run job.sh` | Submit a job |
| `squeue` | `flow list --status running` | View running jobs |
| `squeue -u $USER` | `flow list` | View your jobs |
| `scancel <job_id>` | `flow cancel <task_id>` | Cancel a job |
| `sinfo` | `flow instances` | View available resources |
| `sacct -j <job_id>` | `flow get <task_id>` | Job accounting info |
| `scontrol show job <id>` | `flow describe <task_id>` | Detailed job info |
| `salloc` | `flow run --interactive` | Interactive session |

### Environment Variables

| SLURM Variable | Flow Variable | Description |
|----------------|---------------|-------------|
| `$SLURM_JOB_ID` | `$FLOW_TASK_ID` | Job/task identifier |
| `$SLURM_ARRAY_TASK_ID` | `$FLOW_TASK_INDEX` | Array task index |
| `$SLURM_NTASKS` | `$FLOW_NUM_INSTANCES` | Number of tasks |
| `$SLURM_NODELIST` | `$FLOW_INSTANCE_IPS` | List of nodes/instances |
| `$SLURM_JOB_NAME` | `$FLOW_TASK_NAME` | Job name |
| `$SLURM_SUBMIT_DIR` | `$FLOW_SUBMIT_DIR` | Submission directory |

## SLURM Script Compatibility

### Direct SLURM Script Execution

Flow can run SLURM scripts with automatic translation:

```bash
# Run existing SLURM script
flow run --slurm my-job.slurm

# With modifications
flow run --slurm my-job.slurm --instance-type a100 --max-price 5.00
```

### Example SLURM Script

```bash
#!/bin/bash
#SBATCH --job-name=pytorch-training
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --mem=32G
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

module load cuda/11.8
module load python/3.10

cd $SLURM_SUBMIT_DIR
python train.py --epochs 100 --batch-size 32
```

### Translated Flow Script

```bash
#!/bin/bash
# Flow equivalent of SLURM script above

flow run \
    --name "pytorch-training" \
    --instance-type "a100" \
    --max-runtime "2h" \
    --output-dir "logs" \
    --command "python train.py --epochs 100 --batch-size 32"
```

## Array Jobs

### SLURM Array Job

```bash
#!/bin/bash
#SBATCH --array=0-99
#SBATCH --job-name=param-sweep

python experiment.py --config configs/exp_${SLURM_ARRAY_TASK_ID}.json
```

### Flow Array Job

```bash
# Submit array job
flow run-array \
    --array-size 100 \
    --name "param-sweep" \
    --instance-type "a100" \
    --command 'python experiment.py --config configs/exp_${FLOW_TASK_INDEX}.json'

# Or using a loop
for i in {0..99}; do
    flow run \
        --name "param-sweep-$i" \
        --instance-type "a100" \
        --env TASK_INDEX=$i \
        --command "python experiment.py --config configs/exp_$i.json"
done
```

## MPI and Distributed Jobs

### SLURM MPI Job

```bash
#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:4

mpirun -np 16 python distributed_train.py
```

### Flow Distributed Job

```bash
# Multi-instance distributed training
flow run \
    --name "distributed-training" \
    --instance-type "4xa100" \
    --num-instances 4 \
    --command "torchrun --nproc_per_node=4 --nnodes=4 distributed_train.py"
```

## Resource Specifications

### SLURM to Flow Resource Mapping

| SLURM Directive | Flow Option | Example |
|-----------------|-------------|---------|
| `--gres=gpu:1` | `--instance-type a100` | Single GPU |
| `--gres=gpu:4` | `--instance-type 4xa100` | Multi-GPU |
| `--mem=64G` | (included in instance) | Memory included |
| `--time=24:00:00` | `--max-runtime 24h` | Time limit |
| `--partition=gpu` | (automatic) | GPU partition |

### Instance Type Selection

```bash
# SLURM: Request specific GPU
#SBATCH --gres=gpu:a100:1

# Flow: Select by GPU type
flow run --instance-type a100 command.sh

# Mithril GPU mappings:
# 1× A100 80GB: --instance-type a100
# 2× A100 80GB: --instance-type 2xa100
# 4× A100 80GB: --instance-type 4xa100
# 8× A100 80GB: --instance-type 8xa100
# 8× H100 80GB: --instance-type h100
```

## Dependencies and Modules

### SLURM Modules

```bash
# SLURM script
module load cuda/11.8
module load python/3.10
module load pytorch/2.0
```

### Flow Approach

```bash
# Option 1: Include in command
flow run --command "
    # Install dependencies
    pip install torch torchvision
    
    # Run training
    python train.py
"

# Option 2: Use container
flow run \
    --container "pytorch/pytorch:2.0.0-cuda11.8-cudnn8" \
    --command "python train.py"

# Option 3: Requirements file
flow run --command "
    pip install -r requirements.txt
    python train.py
"
```

## Output and Logging

### SLURM Output Handling

```bash
#SBATCH --output=logs/job_%j.out
#SBATCH --error=logs/job_%j.err
```

### Flow Output Handling

```bash
# Automatic logging
flow run command.sh  # Logs available via API/CLI

# Custom output directory
flow run \
    --output-dir logs \
    --command "python train.py > output.log 2>&1"

# View logs
flow logs <task_id>
flow logs <task_id> --follow
flow logs <task_id> --tail 100
```

## Job Dependencies

### SLURM Dependencies

```bash
# Job dependency
sbatch --dependency=afterok:12345 job2.sh
```

### Flow Dependencies

```bash
# Wait for task completion
TASK1=$(flow run --name "preprocess" command1.sh)
flow wait $TASK1
TASK2=$(flow run --name "train" --depends-on $TASK1 command2.sh)

# Or programmatically
flow run \
    --name "pipeline" \
    --command "
        # Run preprocessing
        python preprocess.py
        
        # Then training
        python train.py
    "
```

## Interactive Sessions

### SLURM Interactive

```bash
salloc --gres=gpu:1 --time=2:00:00
srun --pty bash
```

### Flow Interactive

```bash
# Start interactive session
flow run --interactive --instance-type a100

# SSH directly to running instance
flow ssh <task_id>

# Port forwarding for Jupyter
flow run \
    --interactive \
    --instance-type a100 \
    --ports 8888 \
    --command "jupyter lab --ip=0.0.0.0"
```

## Cost Management

### New in Flow: Cost Controls

```bash
# Set maximum price per hour
flow run \
    --max-price 5.00 \
    --instance-type a100 \
    command.sh

# Use spot instances (70% savings)
flow run \
    --spot \
    --instance-type a100 \
    command.sh

# Set total budget
flow run \
    --max-total-cost 100.00 \
    --instance-type 8xa100 \
    long_training.sh
```

## Migration Script

### Automated SLURM Script Converter

```python
#!/usr/bin/env python3
"""Convert SLURM scripts to Flow commands."""

import re
import sys

def convert_slurm_to_flow(slurm_script):
    """Convert SLURM script to Flow command."""
    
    flow_cmd = ["flow", "run"]
    
    # Parse SLURM directives
    with open(slurm_script, 'r') as f:
        content = f.read()
    
    # Extract directives
    directives = re.findall(r'#SBATCH\s+(--\S+)(?:\s+(.+))?', content)
    
    for directive, value in directives:
        if directive == "--job-name":
            flow_cmd.extend(["--name", value])
        elif directive == "--gres" and "gpu" in value:
            # Extract GPU count
            gpu_match = re.search(r'gpu:(\d+)', value)
            if gpu_match:
                count = gpu_match.group(1)
                if count == "1":
                    flow_cmd.extend(["--instance-type", "a100"])
                else:
                    flow_cmd.extend(["--instance-type", f"{count}xa100"])
        elif directive == "--time":
            # Convert time format
            flow_cmd.extend(["--max-runtime", value.replace(":", "h")])
        elif directive == "--array":
            # Handle array jobs separately
            print(f"Array job detected: {value}")
            print("Use 'flow run-array' or loop")
    
    # Add the script
    flow_cmd.append(slurm_script)
    
    return " ".join(flow_cmd)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: slurm2flow.py <slurm_script>")
        sys.exit(1)
    
    flow_command = convert_slurm_to_flow(sys.argv[1])
    print("Flow command:")
    print(flow_command)
```

## Best Practices

### 1. **Start Small**
```bash
# Test with a simple job first
flow run --instance-type a100 "nvidia-smi"
```

### 2. **Use Cost Controls**
```bash
# Always set limits
flow run \
    --max-price 5.00 \
    --max-runtime 24h \
    --instance-type a100 \
    train.sh
```

### 3. **Monitor Progress**
```bash
# Watch logs in real-time
flow logs <task_id> --follow

# Check status
flow status
```

### 4. **Handle Failures**
```bash
# Automatic retry
flow run \
    --retry-count 3 \
    --retry-on-failure \
    command.sh
```

## Common Issues

### "No instances available"
```bash
# Try different instance types
flow instances  # List available

# Or increase price limit
flow run --max-price 10.00 ...
```

### "Module not found"
```bash
# Install dependencies in command
flow run --command "
    pip install -r requirements.txt
    python script.py
"
```

### "Permission denied"
```bash
# Check API key
flow whoami

# Reconfigure if needed
flow init
```

## Next Steps

- [CLI Inference Guide](inference.md) - Deploy models via CLI
- [CLI Training Guide](training.md) - Submit training jobs
- [CLI Fine-tuning Guide](fine-tuning.md) - Fine-tune models
- [Command Reference](../../reference/cli.md) - Full CLI documentation