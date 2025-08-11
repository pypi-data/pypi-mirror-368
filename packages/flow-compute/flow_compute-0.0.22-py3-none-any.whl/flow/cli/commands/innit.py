"""British English alias for `init`.

Just displays a short themed greeting and then delegates to the standard init command.
"""

from __future__ import annotations

import click

from flow.cli.commands.init import command as init_command
from flow.cli.utils.theme_manager import theme_manager

# Underlying init click command (reused for options/behavior)
_init_cmd = init_command.get_command()
_console = theme_manager.create_console()


@click.command(
    name="innit",
    help=("British-English alias for init — gets you properly sorted, no faff."),
    context_settings=_init_cmd.context_settings,
    params=_init_cmd.params,
    epilog=_init_cmd.epilog,
    short_help=_init_cmd.short_help,
    add_help_option=_init_cmd.add_help_option,
)
@click.pass_context
def innit(ctx: click.Context, **kwargs):
    """Just runs init with a brief greeting, then delegates to `init`. A bit of joy and humour."""
    accent = theme_manager.get_color("accent")
    default = theme_manager.get_color("default")

    _console.print(f"[{accent}]Right then—shall we? Let's get you set up, sharpish.[/{accent}]")
    _console.print(
        f"[{default}]We'll sort your provider, project, and region — sensible defaults, no faff, job done.[/{default}]"
    )
    _console.print("[dim]Fancy a guided wander? Try 'flow tutorial'. Cheers.[/dim]")

    # Delegate to init
    ctx.invoke(_init_cmd, **kwargs)


class InnitCommand:
    """Expose the `innit` command to the CLI registry."""

    @property
    def name(self) -> str:
        return "innit"

    @property
    def help(self) -> str:
        return "British version of init"

    def get_command(self) -> click.Command:
        return innit


command = InnitCommand()
