#!/usr/bin/env python3
"""Create a GPU task with custom configuration.

This example demonstrates how to:
1. Create a GPU task with custom startup script
2. Configure instance type, region, and pricing
3. Attach persistent storage volumes
4. Monitor task startup and get shell access
5. Use the new user and instance resolution features

Prerequisites:
- Flow SDK installed (`pip install flow-sdk`)
- Mithril API key configured (`flow init`)

How to run:
    # Create a simple H100 task
    python create_gpu_task.py

    # Create with custom instance type
    python create_gpu_task.py --instance-type 8xh100

    # Create with specific region and price limit
    python create_gpu_task.py --region us-west-1 --max-price 50.0

Expected output:
- Creates a GPU task with specified configuration
- Shows task ID and status
- Provides shell connection details
- Monitors startup progress
"""

import flow
from flow import Flow, TaskConfig
import sys
import argparse
import time


def main():
    """Create a GPU task with custom configuration."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Create a GPU task")
    parser.add_argument(
        "--instance-type", default="h100", help="GPU instance type (e.g., h100, a100, 8xh100)"
    )
    parser.add_argument("--region", default=None, help="Preferred region (e.g., us-west-1)")
    parser.add_argument(
        "--max-price", type=float, default=50.0, help="Maximum price per hour in USD"
    )
    parser.add_argument("--name", default="gpu-training-task", help="Task name")
    parser.add_argument(
        "--docker", default=None, help="Docker image to use (e.g., pytorch/pytorch:latest)"
    )
    parser.add_argument("--volume-size", type=int, default=100, help="Storage volume size in GB")

    args = parser.parse_args()

    # Create startup script
    startup_script = f"""#!/bin/bash
set -e

echo "=== GPU Task Starting ==="
echo "Time: $(date)"
echo "Hostname: $(hostname)"
echo ""

# System information
echo "=== System Information ==="
uname -a
echo "CPU cores: $(nproc)"
echo "Memory: $(free -h | grep '^Mem:' | awk '{{print $2}}')"
echo ""

# GPU information
echo "=== GPU Information ==="
nvidia-smi
echo ""

# Storage setup
echo "=== Storage Setup ==="
df -h /volumes/data
echo ""

# Install Python packages if needed
echo "=== Environment Setup ==="
if command -v python3 &> /dev/null; then
    python3 --version
    pip3 install --upgrade pip
    pip3 install numpy torch torchvision transformers
else
    echo "Python not found, installing..."
    apt-get update && apt-get install -y python3 python3-pip
fi

# Create a sample training script
cat > /volumes/data/train.py << 'EOF'
import torch
import time

print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU count:", torch.cuda.device_count())
    for i in range(torch.cuda.device_count()):
        print(f"GPU {{i}}: {{torch.cuda.get_device_name(i)}}")
    
    # Simple GPU benchmark
    print("\\nRunning GPU benchmark...")
    device = torch.device("cuda")
    size = 10000
    x = torch.randn(size, size, device=device)
    y = torch.randn(size, size, device=device)
    
    start = time.time()
    z = torch.matmul(x, y)
    torch.cuda.synchronize()
    elapsed = time.time() - start
    
    tflops = 2 * size**3 / elapsed / 1e12
    print(f"Matrix multiplication performance: {{tflops:.2f}} TFLOPS")

print("\\nTraining script ready at /volumes/data/train.py")
EOF

echo ""
echo "=== Task Ready ==="
echo "You can now connect to this instance and run:"
echo "  python3 /volumes/data/train.py"
echo ""
echo "Keeping instance running for interactive work..."

# Keep the instance running
sleep infinity
"""

    # Configure task
    config = TaskConfig(
        name=args.name,
        unique_name=True,
        instance_type=args.instance_type,
        region=args.region,
        max_price_per_hour=args.max_price,
        image=args.docker,
        command=startup_script,
        volumes=[{"name": "data", "size_gb": args.volume_size}],
        # Keep running for interactive work
        max_run_time_hours=8.0,  # Safety limit
    )

    print(f"Creating GPU task...")
    print(f"  Name: {config.name}")
    print(f"  Instance type: {config.instance_type}")
    if config.region:
        print(f"  Region: {config.region}")
    print(f"  Max price: ${config.max_price_per_hour}/hour")
    print(f"  Volume size: {args.volume_size}GB")
    print()

    try:
        # Create Flow client and submit task
        with Flow() as client:
            task = client.run(config, wait=False)
            print(f"✓ Task created successfully!")
            print(f"  Task ID: {task.task_id}")
            print()

            # Monitor startup
            print("Waiting for instance allocation...")
            start_time = time.time()
            last_status = None

            while task.status in ["pending", "provisioning"]:
                if task.status != last_status:
                    print(f"  Status: {task.status}")
                    last_status = task.status

                time.sleep(5)
                task = client.get_task(task.task_id)

                # Timeout after 10 minutes
                if time.time() - start_time > 600:
                    print("⚠ Timeout waiting for instance. Task may still be pending.")
                    break

            if task.status == "running":
                print(f"\n✓ Task is running!")
                print()

                # Show shell access
                if task.shell_command:
                    print("=== Shell Access ===")
                    print(f"Shell Command: {task.shell_command}")
                    print()
                    print("You can also use:")
                    print(f"  flow ssh {task.task_id}")
                    print()

                # Get instance details
                print("=== Instance Details ===")
                try:
                    instances = task.get_instances()
                    for i, inst in enumerate(instances):
                        print(f"Instance {i + 1}:")
                        print(f"  ID: {inst.instance_id}")
                        if inst.public_ip:
                            print(f"  Public IP: {inst.public_ip}")
                except Exception as e:
                    print(f"Could not get instance details: {e}")
                print()

                # Get user info
                print("=== Task Creator ===")
                try:
                    user = task.get_user()
                    if user:
                        print(f"Username: {user.username}")
                        print(f"Email: {user.email}")
                except Exception as e:
                    print(f"Could not get user info: {e}")
                print()

                # Show monitoring commands
                print("=== Monitoring Commands ===")
                print(f"View logs:     flow logs {task.task_id}")
                print(f"Check status:  python check_task_status.py {task.task_id}")
                print(f"Cancel task:   python cancel_task.py {task.task_id}")
                print()

                # Show initial logs
                print("=== Initial Logs ===")
                try:
                    logs = task.logs(tail=30)
                    if logs:
                        for line in logs.splitlines()[-10:]:
                            print(line)
                except Exception:
                    print("Logs not available yet")

                return 0
            else:
                print(f"\n⚠ Unexpected status: {task.status}")
                return 1

    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
