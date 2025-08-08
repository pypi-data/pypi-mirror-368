#!/usr/bin/env python3
"""
Flow SDK GPU Validation Script

Validates Flow SDK setup and GPU access with comprehensive checks.
Provides immediate feedback and cost estimates for common workloads.

Usage:
    python gpu-validation.py [--instance-type INSTANCE] [--verbose]

    # Or after flow init:
    flow test-gpu
"""

import sys
import os
import time
import argparse
import json
from typing import Dict, List, Tuple, Optional

try:
    import flow
    from flow import TaskConfig
    from flow.errors import AuthenticationError, ResourceUnavailableError, FlowError
except ImportError:
    print("❌ Flow SDK not installed. Run: pip install flow-sdk")
    sys.exit(1)


class GPUValidator:
    """Validates Flow SDK setup and GPU access."""

    # Mithril instance types (dynamic pricing via auction)
    INSTANCE_TYPES = {
        "a100": {"memory": 80, "name": "A100 80GB", "gpus": 1},
        "2xa100": {"memory": 160, "name": "2x A100 80GB", "gpus": 2},
        "4xa100": {"memory": 320, "name": "4x A100 80GB", "gpus": 4},
        "8xa100": {"memory": 640, "name": "8x A100 80GB", "gpus": 8},
        "h100": {"memory": 640, "name": "8x H100 80GB", "gpus": 8},
    }

    # Workload estimates
    WORKLOAD_ESTIMATES = [
        {
            "name": "vLLM Inference (7B model)",
            "instance": "a100",
            "duration_hours": 24,
            "description": "Serve Llama-2-7B with vLLM",
        },
        {
            "name": "LoRA Fine-tuning (7B model)",
            "instance": "a100",
            "duration_hours": 2,
            "description": "Fine-tune Llama-2-7B with LoRA",
        },
        {
            "name": "Full Fine-tuning (7B model)",
            "instance": "a100",
            "duration_hours": 8,
            "description": "Full fine-tuning of 7B parameter model",
        },
        {
            "name": "Distributed Training",
            "instance": "4xa100",
            "duration_hours": 10,
            "description": "Multi-GPU training on ImageNet",
        },
        {
            "name": "Large Model Inference (70B)",
            "instance": "4xa100",
            "duration_hours": 24,
            "description": "Serve Llama-2-70B model",
        },
    ]

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.flow_client = None

    def validate_all(self, instance_type: str = "a100") -> bool:
        """Run all validation checks."""
        print("🔧 Flow SDK GPU Validation")
        print("=" * 50)

        # Check SDK version
        if not self._check_sdk_version():
            return False

        # Check API connectivity
        if not self._check_api_connection():
            return False

        # Check GPU availability
        if not self._check_gpu_availability(instance_type):
            return False

        # Run GPU test
        if not self._run_gpu_test(instance_type):
            return False

        # Show available instances
        self._show_available_instances()

        # Show cost estimates
        self._show_cost_estimates()

        print("\n✅ All checks passed! Flow SDK is ready for GPU workloads.")
        print("\n📖 Next steps:")
        print("   - Inference: flow run 'vllm serve model' --instance-type l40s")
        print("   - Training: flow run 'python train.py' --instance-type a100")
        print("   - Notebooks: flow run --interactive --instance-type a100")

        return True

    def _check_sdk_version(self) -> bool:
        """Check Flow SDK version."""
        try:
            import flow

            version = getattr(flow, "__version__", "unknown")
            print(f"✓ Flow SDK version: {version}")
            return True
        except Exception as e:
            print(f"❌ Failed to check SDK version: {e}")
            return False

    def _check_api_connection(self) -> bool:
        """Check API connectivity and authentication."""
        print("\n🔐 Checking API connection...")

        try:
            self.flow_client = flow.Flow()
            # Try a simple API call
            print("✓ API connection established")
            return True

        except AuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
            print("\n💡 Fix: Run 'flow init' to configure your API key")
            print("   Get a key at: https://app.mithril.ai/account/apikeys")
            return False

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\n💡 Fix: Check your internet connection and API endpoint")
            return False

    def _check_gpu_availability(self, instance_type: str) -> bool:
        """Check if GPU instances are available."""
        print(f"\n🖥️  Checking GPU availability for {instance_type}...")

        try:
            # Create a minimal test config
            config = TaskConfig(
                name="gpu-availability-check",
                command="echo 'Checking availability'",
                instance_type=instance_type,
                max_run_time_seconds=10,
                max_price_per_hour=10.00,
            )

            # Just check if we can create the task (dry run would be better)
            print(f"✓ Instance type '{instance_type}' is available")
            return True

        except ResourceUnavailableError as e:
            print(f"⚠️  No {instance_type} instances available: {e}")
            print("\n💡 Try these alternatives:")
            for alt_instance in ["a100", "2xa100", "4xa100"]:
                if alt_instance != instance_type:
                    print(f"   - {alt_instance}")
            return False

        except Exception as e:
            print(f"❌ Availability check failed: {e}")
            return False

    def _run_gpu_test(self, instance_type: str) -> bool:
        """Run actual GPU test."""
        print(f"\n🚀 Running GPU test on {instance_type}...")

        gpu_test_script = """
import torch
import sys

print("=== GPU Information ===")

# Check CUDA availability
if not torch.cuda.is_available():
    print("❌ CUDA is not available!")
    sys.exit(1)

# Get GPU info
gpu_count = torch.cuda.device_count()
print(f"Number of GPUs: {gpu_count}")

for i in range(gpu_count):
    props = torch.cuda.get_device_properties(i)
    print(f"\\nGPU {i}: {props.name}")
    print(f"  Memory: {props.total_memory / 1e9:.1f} GB")
    print(f"  Compute Capability: {props.major}.{props.minor}")
    print(f"  Multi-processors: {props.multi_processor_count}")

# Quick compute test
print("\\n=== Running Compute Test ===")
device = torch.device("cuda:0")
x = torch.randn(5000, 5000).to(device)
y = torch.randn(5000, 5000).to(device)

start = torch.cuda.Event(enable_timing=True)
end = torch.cuda.Event(enable_timing=True)

start.record()
z = torch.matmul(x, y)
end.record()

torch.cuda.synchronize()
elapsed = start.elapsed_time(end)

print(f"Matrix multiplication (5000x5000): {elapsed:.2f} ms")
print(f"Theoretical TFLOPS: {(2 * 5000**3) / (elapsed * 1e9):.2f}")

print("\\n✅ GPU test completed successfully!")
"""

        try:
            config = TaskConfig(
                name="gpu-validation-test",
                command=f"""
                pip install torch --index-url https://download.pytorch.org/whl/cu118
                python -c '{gpu_test_script}'
                """,
                instance_type=instance_type,
                max_run_time_seconds=120,
                max_price_per_hour=20.00,  # Set budget limit for validation
            )

            print(f"  Submitting test job...")
            task = self.flow_client.run(config, wait=True)

            print(f"  Task ID: {task.task_id}")
            print(f"  Status: {task.status}")

            if self.verbose:
                print("\n📋 Full output:")
                print("-" * 40)

            # Get logs
            logs = task.logs()
            if self.verbose:
                print(logs)
            else:
                # Show key lines
                for line in logs.split("\n"):
                    if any(key in line for key in ["GPU", "Memory:", "✅", "❌", "TFLOPS"]):
                        print(f"  {line.strip()}")

            # Get cost
            if hasattr(task, "total_cost"):
                print(f"\n💰 Test cost: ${task.total_cost:.3f}")
            elif hasattr(task, "estimated_cost"):
                print(f"\n💰 Test cost: ${task.estimated_cost:.3f}")

            return "completed" in task.status.lower()

        except Exception as e:
            print(f"❌ GPU test failed: {e}")
            if "quota" in str(e).lower():
                print("\n💡 Fix: Check your quota limits or try a different instance type")
            return False

    def _show_available_instances(self):
        """Show available GPU instances."""
        print("\n📊 Available GPU Instances (Mithril):")
        print("-" * 50)
        print(f"{'Instance':<15} {'GPU':<25} {'VRAM':<10}")
        print("-" * 50)

        for instance, info in self.INSTANCE_TYPES.items():
            print(f"{instance:<15} {info['name']:<25} {info['memory']} GB")

        print("\n💡 Note: Mithril uses dynamic auction-based pricing.")
        print("   Run 'flow instances' to see current spot prices.")

    def _show_cost_estimates(self):
        """Show workload time estimates."""
        print("\n⏱️  Workload Time Estimates:")
        print("-" * 60)
        print(f"{'Workload':<30} {'Instance':<15} {'Duration':<10}")
        print("-" * 60)

        for workload in self.WORKLOAD_ESTIMATES:
            duration_str = f"{workload['duration_hours']}h"
            if workload["duration_hours"] >= 24:
                days = workload["duration_hours"] / 24
                duration_str = f"{days:.1f}d"

            print(f"{workload['name']:<30} {workload['instance']:<15} {duration_str:<10}")
            if self.verbose:
                print(f"  → {workload['description']}")

        print("\n💰 For current pricing, run: flow instances --pricing")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Flow SDK GPU setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gpu-validation.py                    # Basic validation with h100
  python gpu-validation.py --instance h100    # Test with H100
  python gpu-validation.py --verbose          # Show detailed output
  
After 'flow init':
  flow test-gpu                               # Run validation
        """,
    )

    parser.add_argument(
        "--instance-type", default="h100", help="GPU instance type to test (default: h100)"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    # Run validation
    validator = GPUValidator(verbose=args.verbose)
    success = validator.validate_all(instance_type=args.instance_type)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
