"""Example command - Run or display the gpu-test example.

This module implements the "example" command for the Flow CLI. For now, we
ship a single, focused example that verifies GPU access via ``nvidia-smi``.
You can either run it directly or print its YAML configuration.

Command Usage:
    flow example [gpu-test] [--show]

Examples:
    List available examples:
        $ flow example

    Run the example directly:
        $ flow example gpu-test

    Show example configuration:
        $ flow example gpu-test --show

The command will:
- List the example when called without arguments
- Run the example task when given the name (default behavior)
- Display the YAML configuration when --show flag is used
- Submit tasks to available GPU infrastructure
- Return task ID and status for monitoring

Note:
    Running examples requires valid Flow configuration and credentials.
"""

from typing import Optional

import click
import yaml

from flow import Flow
from flow.api.models import TaskConfig
from .base import BaseCommand, console
from flow.cli.utils.animated_progress import AnimatedEllipsisProgress
from .utils import display_config


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
            """Run the gpu-test example or show its configuration.

            \b
            Examples:
                flow example                 # List examples
                flow example gpu-test        # Run GPU verification example
                flow example gpu-test --show # View configuration

            Use 'flow example --verbose' for detailed descriptions and use cases.
            """
            if verbose and not example_name:
                console.print("\n[bold]Flow SDK Example Task:[/bold]\n")
                console.print("Available examples:")
                console.print("\n[cyan]gpu-test[/cyan] - GPU verification task")
                console.print("  • Runs nvidia-smi to verify GPU access")
                console.print("  • Displays GPU information")
                console.print("  • Validates CUDA environment\n")
                console.print("Usage:")
                console.print("  flow example gpu-test --show   # View YAML")
                console.print("  flow example gpu-test         # Run the example\n")
                console.print("Next steps:")
                console.print("  • Monitor progress: flow status")
                console.print("  • View output: flow logs <task-name>\n")
                return

            self._execute(example_name, show)

        return example

    def _execute(self, example_name: Optional[str], show: bool = False) -> None:
        """Execute the example command."""
        examples = {
            "gpu-test": {
                "name": "gpu-test",
                "unique_name": True,
                "instance_type": "8xh100",
                "command": '''#!/bin/bash
nvidia-smi && echo "GPU test completed!"''',
                "max_price_per_hour": 1.50,
                "upload_code": False,  # No code upload needed for GPU test
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
                    "Run GPU test: [cyan]flow example gpu-test[/cyan]",
                    "Show configuration: [cyan]flow example gpu-test --show[/cyan]",
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
                    # Show configuration in the same polished table used by `flow run`
                    task_config = TaskConfig(**config)
                    if example_name == "gpu-test":
                        console.print("\n[dim]About this example:[/dim] verifies GPU availability with nvidia-smi.\n")
                    display_config(task_config.model_dump())

                    with AnimatedEllipsisProgress(
                        console, "Submitting task", transient=True
                    ) as progress:
                        # Create TaskConfig from example

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
                            f"Save config: [cyan]flow example {example_name} --show > job.yaml[/cyan]",
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
