#!/bin/bash
#SBATCH --job-name=gpu-verification
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=h100:8
#SBATCH --mem=256G
#SBATCH --time=00:30:00
#SBATCH --output=gpu_verify_%j.out
#SBATCH --error=gpu_verify_%j.err

# Load required modules
module load cuda/12.1
module load python/3.9

# Set up environment
set -euo pipefail

log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }

log "Starting GPU instance verification"

# System information
log "System: $(uname -r), $(nproc) CPUs, $(free -h | grep Mem | awk '{print $2}') RAM"

# GPU verification
if ! command -v nvidia-smi &> /dev/null; then
    log "ERROR: nvidia-smi not found"
    exit 1
fi

nvidia-smi --query-gpu=name,memory.total,compute_mode --format=csv
log "GPU count: $(nvidia-smi -L | wc -l)"

# CUDA test
if command -v python3 &> /dev/null; then
    python3 -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')
" 2>/dev/null || log "PyTorch not available"
fi

# Storage verification  
log "Storage:"
df -h | grep -E '(^Filesystem|/volumes)'

if [ -d "/volumes/test" ]; then
    testfile="/volumes/test/verify_$(date +%s).txt"
    echo "test" > "$testfile" && log "Volume write: OK" || log "Volume write: FAILED"
    rm -f "$testfile"
else
    log "WARNING: Volume not mounted at /volumes/test"
fi

log "Verification complete"