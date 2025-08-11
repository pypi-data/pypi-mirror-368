"""Common CLI message helpers to keep output consistent across commands.

Minimal helpers only; aim to reduce duplication without introducing heavy abstractions.
"""

from __future__ import annotations

from collections.abc import Iterable

from rich.console import Console

from flow.cli.commands.feedback import feedback


def print_next_actions(console: Console, actions: Iterable[str]) -> None:
    """Print a small, consistent next-steps block.

    This preserves existing look-and-feel but centralizes formatting.
    """
    actions = list(actions or [])
    if not actions:
        return
    console.print("\n[dim]Next steps:[/dim]")
    for action in actions:
        console.print(f"  • {action}")


def print_yaml_usage_hint(example_name: str) -> None:
    """Show a compact info panel on how to save and submit YAML configs."""
    message = (
        "Save this to a file and submit:\n"
        f"  flow example {example_name} --show > job.yaml\n"
        "  flow run job.yaml"
    )
    feedback.info(message, title="How to use this config")


def print_submission_success(
    console: Console,
    task_ref: str,
    instance_type: str | None,
    commands: Iterable[str],
    warnings: Iterable[str] | None = None,
    subtitle: str | None = "You can safely exit and run the commands later",
) -> None:
    """Render a compact success panel after submission with commands and warnings."""
    lines = [
        f"[bold]{task_ref}[/bold]"
        + (f" on [accent]{instance_type}[/accent]" if instance_type else ""),
        "",
        "Commands:",
        "\n".join(list(commands)),
    ]
    warnings = list(warnings or [])
    if warnings:
        lines.extend(["", "[yellow]Warnings:[/yellow]"] + [f"  {w}" for w in warnings])
    feedback.success("\n".join(lines), title="Task submitted", subtitle=subtitle)
