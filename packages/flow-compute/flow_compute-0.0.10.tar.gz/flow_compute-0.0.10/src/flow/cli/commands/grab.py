"""Grab command - Quickly acquire GPU resources for interactive use.

This module implements the grab command for the Flow CLI. It provides a
simplified interface for acquiring GPU resources without the task abstraction,
perfect for interactive development and exploration.

Examples:
    # Grab 8 GPUs of any type
    $ flow grab 8

    # Grab specific GPU type and count
    $ flow grab 256 h100

    # Grab with time limit
    $ flow grab 64 a100 --hours 4

    # Grab with price constraint
    $ flow grab 128 h100 --max-price 2.50

Command Usage:
    flow grab COUNT [GPU_TYPE] [OPTIONS]

The command will:
- Calculate optimal instance configuration
- Acquire resources from the provider
- Set up SSH access
- Display connection information
- Track grabbed resources for easy release

Note:
    Use 'flow release' to free grabbed resources.
    Default duration is 1 hour to prevent accidental long-running allocations.
"""

import json

import click

from flow import Flow, TaskConfig
from flow.errors import AuthenticationError, ValidationError

from .base import BaseCommand, console
from .utils import wait_for_task


class GrabCommand(BaseCommand):
    """Quickly grab GPU resources for interactive use."""

    @property
    def name(self) -> str:
        return "grab"

    @property
    def help(self) -> str:
        return """Quickly grab GPU resources for interactive development
        
        Example: flow grab 256 h100"""

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.argument("count", type=int)
        @click.argument("gpu_type", required=False, default=None)
        @click.option(
            "--hours",
            type=float,
            help="Maximum runtime in hours",
        )
        @click.option(
            "--days",
            "-d",
            type=float,
            help="Maximum runtime in days",
        )
        @click.option(
            "--weeks",
            "-w",
            type=float,
            help="Maximum runtime in weeks",
        )
        @click.option(
            "--months",
            "-m",
            type=float,
            help="Maximum runtime in months (30 days)",
        )
        @click.option(
            "--max-price",
            "-p",
            type=float,
            help="Maximum price per GPU/hour in USD",
        )
        @click.option(
            "--ssh-keys",
            "-k",
            multiple=True,
            help="SSH keys to authorize (can specify multiple)",
        )
        @click.option(
            "--region",
            "-r",
            help="Preferred region (e.g., us-west-2)",
        )
        @click.option(
            "--run",
            help="Command to run after grabbing resources",
        )
        @click.option(
            "--name",
            "-n",
            help="Custom name for the grabbed resources",
        )
        @click.option(
            "--no-unique",
            is_flag=True,
            help="Don't append unique suffix to resource name",
        )
        @click.option(
            "--json",
            "output_json",
            is_flag=True,
            help="Output JSON for automation",
        )
        @click.option(
            "--verbose",
            "-v",
            is_flag=True,
            help="Show detailed usage patterns and pricing info",
        )
        def grab(
            count: int,
            gpu_type: str | None,
            hours: float | None,
            days: float | None,
            weeks: float | None,
            months: float | None,
            max_price: float | None,
            ssh_keys: tuple[str, ...],
            region: str | None,
            run: str | None,
            name: str | None,
            no_unique: bool,
            output_json: bool,
            verbose: bool,
        ):
            """Grab GPU resources for interactive use.

            COUNT: Number of GPUs to grab
            GPU_TYPE: Type of GPU (e.g., h100, a100). If not specified, any available type.

            \b
            Examples:
                flow grab 8                  # 8 GPUs, any type, 1 hour
                flow grab 8 h100             # 8 H100 GPUs specifically
                flow grab 32 a100 --hours 4  # 32 A100s for 4 hours
                flow grab 1 --name notebook  # Named single GPU

            Use 'flow grab --verbose' for advanced patterns and pricing guidance.
            """
            if verbose:
                console.print("\n[bold]GPU Grab Patterns & Pricing:[/bold]\n")
                console.print("Quick allocations:")
                console.print("  flow grab 8                       # Any available GPU type")
                console.print("  flow grab 8 h100                  # Specific GPU type")
                console.print("  flow grab 128 h100 --hours 24     # Large cluster")
                console.print("  flow grab 1 --name jupyter        # Named for easy reference\n")

                console.print("Duration options:")
                console.print("  flow grab 8 --hours 2             # 2 hours")
                console.print("  flow grab 8 --days 1              # 24 hours")
                console.print("  flow grab 8 --weeks 1             # 7 days")
                console.print("  flow grab 8 --months 1            # 30 days\n")

                console.print("Cost optimization:")
                console.print("  flow grab 32 --max-price 2.00     # Max $2/GPU/hour")
                console.print("  flow grab 8 a10g                  # Budget GPU option")
                console.print("  flow grab 8 --region us-east-1    # Specific region\n")

                console.print("Common workflows:")
                console.print("  # Grab and connect immediately")
                console.print("  flow grab 8 && flow ssh grab-*")
                console.print("  ")
                console.print("  # Run command after grabbing")
                console.print("  flow grab 8 --run 'nvidia-smi'")
                console.print("  ")
                console.print("  # Interactive notebook")
                console.print("  flow grab 1 --name notebook && flow ssh notebook -c 'jupyter lab'")
                console.print("  ")
                console.print("  # Multi-node cluster")
                console.print("  flow grab 64 --name cluster       # Creates 8 nodes")
                console.print("  flow ssh cluster --node 0          # SSH to first node")
                console.print("  flow ssh cluster --node 7          # SSH to last node\n")

                console.print("Instance configurations:")
                console.print("  • 1 GPU   → Single GPU instance")
                console.print("  • 8 GPUs  → Standard multi-GPU node")
                console.print("  • 64 GPUs → 8 nodes of 8 GPUs each")
                console.print("  • Custom counts rounded to instance sizes\n")

                console.print("Next steps after grab:")
                console.print("  • Connect: flow ssh <grab-name>")
                console.print("  • Multi-node: flow ssh <grab-name> --node <0-N>")
                console.print("  • Release: flow release <grab-name>")
                console.print("  • Check status: flow status <grab-name>\n")
                return

            # Handle the rest of the logic
            self._execute(
                count,
                gpu_type,
                hours,
                days,
                weeks,
                months,
                max_price,
                ssh_keys,
                region,
                run,
                name,
                no_unique,
                output_json,
            )

        return grab

    def _execute(
        self,
        count: int,
        gpu_type: str | None,
        hours: float | None,
        days: float | None,
        weeks: float | None,
        months: float | None,
        max_price: float | None,
        ssh_keys: tuple[str, ...],
        region: str | None,
        run: str | None,
        name: str | None,
        no_unique: bool,
        output_json: bool,
    ) -> None:
        """Execute the grab command."""
        # Start progress animation
        progress = None
        if not output_json:
            from ..utils.animated_progress import AnimatedEllipsisProgress

            progress = AnimatedEllipsisProgress(
                console,
                f"Acquiring {count} GPU{'s' if count != 1 else ''}",
                start_immediately=True,
                transient=True,
            )

        try:
            # Validate inputs
            if count <= 0:
                self.handle_error("GPU count must be positive")
                return

            # Convert all time units to hours
            total_hours = self._calculate_total_hours(hours, days, weeks, months)

            if total_hours is not None:
                if total_hours <= 0:
                    self.handle_error("Duration must be positive")
                    return
                if total_hours > 168:  # Warn but don't block
                    console.print(
                        "[yellow]Note: Maximum supported duration is typically 168 hours (7 days)[/yellow]"
                    )

            # Calculate optimal instance configuration
            instance_type, num_instances = self._calculate_optimal_config(count, gpu_type)

            # Generate name if not provided
            if not name:
                from ..utils.name_generator import generate_unique_name

                name = generate_unique_name(prefix="grab", base_name=None, add_unique=not no_unique)
            # If name is provided, use it as-is

            # Create config for resource allocation
            config_dict = {
                "name": name,
                "unique_name": False,  # We handle uniqueness ourselves with --no-unique
                "instance_type": instance_type,
                "num_instances": num_instances,
                "command": run if run else ["sleep", "infinity"],
                "image": "nvidia/cuda:12.1.0-runtime-ubuntu22.04",
                "env": {
                    "FLOW_GRAB": "true",
                    "FLOW_GPU_COUNT": str(count),
                    "FLOW_GPU_TYPE": gpu_type or "any",
                },
            }

            # Add max_run_time_hours if specified
            if total_hours is not None:
                config_dict["max_run_time_hours"] = total_hours

            # Add optional parameters
            if ssh_keys:
                config_dict["ssh_keys"] = list(ssh_keys)
            if max_price:
                config_dict["max_price_per_hour"] = max_price * count  # Total price
            if region:
                config_dict["region"] = region

            config = TaskConfig(**config_dict)

            # Initialize Flow client and submit
            flow_client = Flow()

            if not output_json:
                # Show what we're doing
                console.print("\n[bold]Configuration:[/bold]")
                console.print(f"  GPUs: {count}x {gpu_type or 'any'}")
                console.print(f"  Instance config: {num_instances}x {instance_type}")
                if total_hours is not None:
                    console.print(f"  Duration: {self._format_duration(total_hours)}")
                if max_price:
                    console.print(
                        f"  Max price: ${max_price:.2f}/GPU/hour (${max_price * count:.2f}/hour total)"
                    )
                console.print()

                # Update progress
                progress.update_message(f"Provisioning {num_instances}x {instance_type}")
                with progress:
                    task = flow_client.run(config)
            else:
                task = flow_client.run(config)

            if output_json:
                result = {
                    "grab_id": task.task_id,
                    "name": name,
                    "gpus": count,
                    "gpu_type": gpu_type or "any",
                    "instance_config": f"{num_instances}x {instance_type}",
                    "status": "provisioning",
                }
                console.print(json.dumps(result))
                return

            # Wait for resources to be ready
            status = wait_for_task(
                flow_client, task.task_id, watch=False, json_output=False, task_name=task.name
            )

            if status == "running":
                # Get updated task info
                task = flow_client.get_task(task.task_id)

                console.print("\n[green]✓[/green] Resources acquired successfully!")
                console.print(f"\nCluster: [cyan]{name}[/cyan]")
                console.print(
                    f"GPUs: {count}x {gpu_type or 'any'} ({num_instances} node{'s' if num_instances > 1 else ''})"
                )

                # Show pricing information
                if (
                    hasattr(task, "cost_per_hour")
                    and task.cost_per_hour
                    and task.cost_per_hour != "$0"
                ):
                    console.print(f"Cost: {task.cost_per_hour}/hour")

                # Show the price limit if it was specified by the user
                if max_price:
                    console.print(
                        f"Price limit: ${max_price:.2f}/GPU/hour (${max_price * count:.2f}/hour total)"
                    )

                console.print(f"\nSSH access: [cyan]flow ssh {name}[/cyan]")
                if num_instances > 1:
                    console.print(
                        f"Multi-node access: [cyan]flow ssh {name} --node <0-{num_instances - 1}>[/cyan]"
                    )

                if total_hours is not None:
                    console.print(
                        f"\n[yellow]Resources will remain allocated for up to {self._format_duration(total_hours)}.[/yellow]"
                    )
                else:
                    console.print(
                        "\n[yellow]Resources will remain allocated until manually released.[/yellow]"
                    )
                console.print(f"To release: [cyan]flow release {name}[/cyan]")

                if run:
                    console.print(f"\n[dim]Running command: {run}[/dim]")
            elif status == "failed":
                console.print("\n[red]✗[/red] Failed to acquire resources")
                console.print("Try adjusting your requirements or check availability")
            else:
                console.print(f"\n[yellow]![/yellow] Unexpected status: {status}")

        except AuthenticationError:
            self.handle_auth_error()
        except ValidationError as e:
            self.handle_error(f"Invalid configuration: {e}")
        except Exception as e:
            self.handle_error(str(e))
        finally:
            if progress and progress._active:
                progress.__exit__(None, None, None)

    def _calculate_optimal_config(self, gpu_count: int, gpu_type: str | None) -> tuple[str, int]:
        """Calculate optimal instance type and count for requested GPUs.

        Args:
            gpu_count: Total number of GPUs requested
            gpu_type: Type of GPU (e.g., 'h100', 'a100') or None for any

        Returns:
            Tuple of (instance_type, num_instances)
        """
        # Get the current provider from config
        from flow import Flow

        # Create a temporary Flow client to access the provider
        flow_client = Flow()
        provider = flow_client.provider  # Use the public property

        # Use provider's normalize method for provider-specific constraints
        instance_type, num_instances, warning = provider.normalize_instance_request(
            gpu_count, gpu_type
        )

        # Display any warning about adjustments
        if warning:
            console.print(f"[yellow]Note: {warning}[/yellow]")

        return instance_type, num_instances

    def _calculate_total_hours(
        self,
        hours: float | None,
        days: float | None,
        weeks: float | None,
        months: float | None,
    ) -> float | None:
        """Calculate total hours from various time units.

        Args:
            hours: Hours specified
            days: Days specified (converted to hours)
            weeks: Weeks specified (converted to hours)
            months: Months specified (converted to 30-day months)

        Returns:
            Total hours or None if no duration specified
        """
        # Check that only one time unit is specified
        time_args = [arg for arg in [hours, days, weeks, months] if arg is not None]
        if len(time_args) > 1:
            self.handle_error(
                "Please specify only one time unit (--hours, --days, --weeks, or --months)"
            )
            return None

        if not time_args:
            return None

        # Convert to hours
        if hours is not None:
            return hours
        elif days is not None:
            return days * 24
        elif weeks is not None:
            return weeks * 7 * 24
        elif months is not None:
            return months * 30 * 24  # Approximate month as 30 days

        return None

    def _format_duration(self, total_hours: float) -> str:
        """Format duration in human-readable form.

        Args:
            total_hours: Duration in hours

        Returns:
            Formatted string like "2 days", "1 week", "3.5 hours"
        """
        if total_hours >= 24 * 30:  # More than a month
            months = total_hours / (24 * 30)
            return f"{months:.1f} month{'s' if months != 1 else ''}"
        elif total_hours >= 24 * 7:  # More than a week
            weeks = total_hours / (24 * 7)
            return f"{weeks:.1f} week{'s' if weeks != 1 else ''}"
        elif total_hours >= 24:  # More than a day
            days = total_hours / 24
            return f"{days:.1f} day{'s' if days != 1 else ''}"
        else:
            return f"{total_hours:.1f} hour{'s' if total_hours != 1 else ''}"


# Export command instance
command = GrabCommand()
