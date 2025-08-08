#!/bin/bash
#SBATCH --job-name=ml-training
#SBATCH --partition=gpu
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --gpus-per-node=a100:4
#SBATCH --mem=256G
#SBATCH --time=12:00:00
#SBATCH --output=training_%A_%a.out
#SBATCH --error=training_%A_%a.err
#SBATCH --array=1-3
#SBATCH --export=EXPERIMENT_ID=exp001,DATA_PATH=/data/imagenet

# Load required modules
module load cuda/12.1
module load python/3.10
module load openmpi/4.1.0

# Set up environment
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export NCCL_DEBUG=INFO

# Log node information
echo "Running on node: $(hostname)"
echo "Array task ID: $SLURM_ARRAY_TASK_ID"
echo "Total nodes: $SLURM_NNODES"
echo "GPUs per node: 4"

# Change to working directory
cd /workspace

# Run distributed training with different hyperparameters per array task
case $SLURM_ARRAY_TASK_ID in
    1) LR=0.001 ;;
    2) LR=0.01 ;;
    3) LR=0.1 ;;
esac

# Launch distributed training
srun python -m torch.distributed.launch \
    --nproc_per_node=4 \
    --nnodes=$SLURM_NNODES \
    --node_rank=$SLURM_NODEID \
    --master_addr=$SLURM_SUBMIT_HOST \
    --master_port=29500 \
    train_distributed.py \
    --model resnet50 \
    --batch-size 256 \
    --epochs 100 \
    --lr $LR \
    --data-path $DATA_PATH \
    --experiment-id "${EXPERIMENT_ID}_lr${LR}"

# Save results
echo "Training completed for learning rate: $LR"