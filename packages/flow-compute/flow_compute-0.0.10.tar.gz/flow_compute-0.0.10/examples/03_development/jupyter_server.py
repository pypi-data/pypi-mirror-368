#!/usr/bin/env python3
"""Interactive Jupyter server on GPU.

Launches a Jupyter notebook server with GPU access and ML libraries.

Prerequisites:
    - Flow SDK configured (`flow init`)
    - Valid API credentials

Usage:
    python 02_jupyter_server.py

Access:
    Shell tunnel required for security (direct HTTP not supported)
    Instructions provided after launch
"""

import secrets
import sys
import time
from pathlib import Path

from flow import Flow, TaskConfig
from flow.api.models import TaskStatus


def main():
    """Launch Jupyter notebook server on GPU."""
    # Generate secure access token
    jupyter_token = secrets.token_urlsafe(32)

    # Create welcome notebook content
    welcome_notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Flow SDK Jupyter Server\n",
                    "GPU-accelerated notebook environment\n\n",
                    "## Quick Start\n",
                    "Run the cells below to verify GPU access and performance.",
                ],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "import torch\n",
                    "print(f'PyTorch {torch.__version__}')\n",
                    "print(f'CUDA available: {torch.cuda.is_available()}')\n",
                    "if torch.cuda.is_available():\n",
                    "    print(f'GPU: {torch.cuda.get_device_name(0)}')\n",
                    "    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')",
                ],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# GPU performance test\n",
                    "if torch.cuda.is_available():\n",
                    "    size = 10000\n",
                    "    x = torch.randn(size, size, device='cuda')\n",
                    "    torch.cuda.synchronize()\n",
                    "    import time\n",
                    "    start = time.time()\n",
                    "    y = torch.matmul(x, x)\n",
                    "    torch.cuda.synchronize()\n",
                    "    elapsed = time.time() - start\n",
                    "    tflops = 2 * size**3 / elapsed / 1e12\n",
                    "    print(f'Matrix multiply {size}x{size}: {tflops:.1f} TFLOPS')",
                ],
            },
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    # Jupyter setup script
    jupyter_script = f"""#!/bin/bash
set -euo pipefail

# Install dependencies
apt-get update -qq
apt-get install -y python3-pip > /dev/null

# Install Jupyter and ML libraries
pip3 install -q jupyter notebook ipykernel
pip3 install -q numpy pandas matplotlib torch torchvision scikit-learn

# Setup notebook directory
mkdir -p /volumes/notebooks
cd /volumes/notebooks

# Create welcome notebook
cat > Welcome.ipynb << 'EOF'
{welcome_notebook}
EOF

# Start Jupyter server
echo "Starting Jupyter server..."
exec jupyter notebook \\
    --ip=0.0.0.0 \\
    --port=8888 \\
    --no-browser \\
    --allow-root \\
    --NotebookApp.token='{jupyter_token}' \\
    --NotebookApp.notebook_dir=/volumes/notebooks
"""

    # Task configuration
    config = TaskConfig(
        name="jupyter-server",
        unique_name=True,
        instance_type="h100-80gb.sxm.8x",
        region="us-central1-b",
        max_price_per_hour=98.32,  # H100x8 pricing
        command=jupyter_script,
        volumes=[{"name": "notebooks", "size_gb": 50, "mount_path": "/volumes/notebooks"}],
        auto_terminate=False,  # Keep running
        max_run_time_hours=8.0,  # Safety limit
    )

    print(f"Launching Jupyter server: {config.instance_type} @ ${config.max_price_per_hour}/hr")

    try:
        with Flow() as flow_client:
            # Submit task
            task = flow_client.run(config)
            print(f"Task ID: {task.task_id}")

            # Wait for running state
            print("\nWaiting for instance...")
            while task.status == TaskStatus.PENDING:
                time.sleep(5)
                task.refresh()

            if task.status != TaskStatus.RUNNING:
                print(f"\n✗ Unexpected status: {task.status}")
                return 1

            # Get connection info
            public_ip = task.public_ip or task.host
            ssh_key = Path.home() / ".flow" / "ssh" / "flow-key"

            # Display access instructions
            print("\n" + "=" * 60)
            print("JUPYTER SERVER READY")
            print("=" * 60)
            print(f"\nTask ID: {task.task_id}")
            print(f"\nShell tunnel command:")
            print(f"  ssh -L 8888:localhost:8888 -i {ssh_key} ubuntu@{public_ip}")
            print(f"\nJupyter URL:")
            print(f"  http://localhost:8888/?token={jupyter_token}")
            print(f"\nMonitor logs:")
            print(f"  flow logs {task.task_id} --follow")
            print(f"\nStop server:")
            print(f"  flow cancel {task.task_id}")
            print("=" * 60)

            # Show startup logs
            print("\nStartup logs:")
            logs = task.logs(tail=20)
            print(logs)

            return 0

    except Exception as e:
        print(f"\nError: {e}")
        if "api key" in str(e).lower():
            print("Configure credentials: flow init")
        return 1


if __name__ == "__main__":
    sys.exit(main())
