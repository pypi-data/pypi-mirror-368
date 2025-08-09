"""Example command - Run or display example task configurations.

This module implements the example command for the Flow CLI. It provides users
with pre-configured task examples that demonstrate various features and common
use cases of the Flow SDK. Examples can be run directly or their configurations
can be displayed for customization.

Command Usage:
    flow example [EXAMPLE_NAME] [--show]

Examples:
    List all available examples:
        $ flow example

    Run an example directly:
        $ flow example minimal
        $ flow example gpu-test

    Show example configuration:
        $ flow example minimal --show

    Save configuration for customization:
        $ flow example training --show > my-job.yaml
        $ flow run my-job.yaml

The command will:
- List all available examples when called without arguments
- Run the example task when given a name (default behavior)
- Display the YAML configuration when --show flag is used
- Submit tasks to available GPU infrastructure
- Return task ID and status for monitoring

Available examples include:
- minimal: Basic GPU task with simple commands
- gpu-test: GPU verification with nvidia-smi
- system-info: Comprehensive system information gathering
- training: Multi-GPU training simulation with volumes

Note:
    Running examples requires valid Flow configuration and credentials.
    Use --show to view configurations before running.
"""

from typing import Optional

import click
import yaml

from flow import Flow
from flow.api.models import TaskConfig
from .base import BaseCommand, console
from flow.cli.utils.animated_progress import AnimatedEllipsisProgress


class ExampleCommand(BaseCommand):
    """Run example tasks or show their configuration."""

    @property
    def name(self) -> str:
        return "example"

    @property
    def help(self) -> str:
        return "Run example GPU tasks - quick demos and templates"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.argument("example_name", required=False)
        @click.option("--show", is_flag=True, help="Show YAML configuration instead of running")
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed example descriptions")
        def example(example_name: Optional[str] = None, show: bool = False, verbose: bool = False):
            """Run example tasks or show their configuration.

            \b
            Examples:
                flow example                 # List all examples
                flow example minimal         # Run minimal example
                flow example gpu-test --show # View configuration

            Use 'flow example --verbose' for detailed descriptions and use cases.
            """
            if verbose and not example_name:
                console.print("\n[bold]Flow SDK Example Tasks:[/bold]\n")
                console.print("Available examples:")
                console.print("\n[cyan]minimal[/cyan] - Basic GPU task demonstration")
                console.print("  • Simple hello world on GPU instance")
                console.print("  • Shows basic command execution")
                console.print("  • Good for testing connectivity\n")

                console.print("[cyan]gpu-test[/cyan] - GPU verification task")
                console.print("  • Runs nvidia-smi to verify GPU access")
                console.print("  • Displays GPU information")
                console.print("  • Validates CUDA environment\n")

                console.print("[cyan]system-info[/cyan] - Comprehensive system check")
                console.print("  • Shows CPU, memory, disk details")
                console.print("  • Kernel and OS information")
                console.print("  • GPU configuration summary\n")

                console.print("[cyan]training[/cyan] - Multi-GPU training template")
                console.print("  • Simulates training workflow")
                console.print("  • Demonstrates volume mounting")
                console.print("  • Shows environment variables")
                console.print("  • Progress tracking example\n")

                console.print("Usage patterns:")
                console.print("  # Quick GPU test")
                console.print("  flow example gpu-test")
                console.print("  ")
                console.print("  # Save and customize")
                console.print("  flow example training --show > my-job.yaml")
                console.print("  # Edit my-job.yaml")
                console.print("  flow run my-job.yaml")
                console.print("  ")
                console.print("  # Check example before running")
                console.print("  flow example system-info --show")
                console.print("  flow example system-info\n")

                console.print("Creating custom tasks:")
                console.print("  1. Start with an example: flow example training --show")
                console.print("  2. Modify the YAML configuration")
                console.print("  3. Test locally: flow run config.yaml --dry-run")
                console.print("  4. Submit: flow run config.yaml\n")

                console.print("Next steps:")
                console.print("  • Run your first example: flow example minimal")
                console.print("  • Monitor progress: flow status")
                console.print("  • View output: flow logs <task-name>")
                console.print(
                    "  • Create custom task: flow example training --show > custom.yaml\n"
                )
                return

            self._execute(example_name, show)

        return example

    def _execute(self, example_name: Optional[str], show: bool = False) -> None:
        """Execute the example command."""
        examples = {
            "minimal": {
                "name": "minimal-example",
                "unique_name": True,
                "instance_type": "8xh100",
                "command": """#!/bin/bash
echo "Hello from Flow SDK!" && hostname && date""",
                "max_price_per_hour": 98.32,
            },
            "gpu-test": {
                "name": "gpu-test",
                "unique_name": True,
                "instance_type": "8xh100",
                "command": '''#!/bin/bash
nvidia-smi && echo "GPU test completed!"''',
                "max_price_per_hour": 98.32,
            },
            "system-info": {
                "name": "system-info",
                "unique_name": True,
                "instance_type": "8xh100",
                "command": "bash -c \"echo === System Information ===; echo CPU: $(nproc) cores; echo Memory: $(free -h | grep Mem | awk '{print $2}'); echo Disk: $(df -h / | tail -1 | awk '{print $2}'); echo Kernel: $(uname -r); echo GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo No GPU detected)\"",
                "max_price_per_hour": 98.32,
            },
            "training": {
                "name": "basic-training",
                "unique_name": True,
                "instance_type": "8xh100",
                "max_price_per_hour": 98.32,
                "volumes": [
                    {"size_gb": 100, "mount_path": "/data"},
                    {"size_gb": 50, "mount_path": "/checkpoints"},
                ],
                "environment": {"CUDA_VISIBLE_DEVICES": "0,1", "TF_CPP_MIN_LOG_LEVEL": "2"},
                "command": '''#!/bin/bash
echo "Starting training job..."

# Simulated training loop
for epoch in {1..5}; do
    echo "[$(date)] Epoch $epoch/5"
    sleep 2
done

echo "Training completed!"
echo "Final metrics: accuracy=0.94, loss=0.123"''',
            },
        }

        if example_name is None:
            # List all examples
            console.print("Available examples:")
            for name, config in examples.items():
                console.print(f"  [cyan]{name}[/cyan] - {config.get('name', 'No description')}")
            console.print("\nUsage:")
            console.print("  Run example:        flow example <name>")
            console.print("  Show config:        flow example <name> --show")
            console.print("  Save config:        flow example <name> --show > job.yaml")

            # Show next actions
            self.show_next_actions(
                [
                    "Run minimal example: [cyan]flow example minimal[/cyan]",
                    "Show configuration: [cyan]flow example minimal --show[/cyan]",
                    "Create custom task: [cyan]flow example minimal --show > my-task.yaml[/cyan]",
                ]
            )
        elif example_name in examples:
            config = examples[example_name]

            if show:
                # Show YAML configuration
                yaml_content = yaml.dump(config, default_flow_style=False, sort_keys=False)
                console.print(yaml_content)
            else:
                # Run the example
                console.print(f"Running example: {example_name}")

                try:
                    with AnimatedEllipsisProgress(
                        console, "Submitting task", transient=True
                    ) as progress:
                        # Create TaskConfig from example
                        task_config = TaskConfig(**config)

                        # Initialize Flow and run the task
                        flow = Flow()
                        task = flow.run(task_config)

                    # Use centralized formatter for consistent presentation
                    from flow.cli.utils.task_formatter import TaskFormatter

                    formatter = TaskFormatter()

                    # Add instance type to the submission confirmation
                    instance_type = config.get("instance_type", "default")
                    console.print(f"[green]✓[/green] Task submitted: {task.name} ({instance_type})")

                    # Print remaining info from formatter (commands)
                    lines = formatter.format_post_submit_info(task)
                    for line in lines[1:]:  # Skip first line since we customized it
                        console.print(line)

                    # Show true next steps - what to do after running the example
                    self.show_next_actions(
                        [
                            f"Create custom task: [cyan]flow example {example_name} --show > my-task.yaml[/cyan]",
                        ]
                    )

                except Exception as e:
                    console.print(f"[red]Error running example:[/red] {str(e)}")
                    raise click.exceptions.Exit(1)
        else:
            console.print(f"[red]Error:[/red] Unknown example: {example_name}")
            console.print(f"Available: {', '.join(examples.keys())}")
            raise click.exceptions.Exit(1)


# Export command instance
command = ExampleCommand()
