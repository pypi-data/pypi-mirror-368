"""Innit command - British version of init.

A fun British alias for the init command.
"""

import click

from flow.cli.commands.init import command as init_command

# Get the original init command and create an alias
original_command = init_command.get_command()


@click.command(
    name="innit",
    help="British version of init - Configure Flow SDK credentials and provider settings, innit?",
    context_settings=original_command.context_settings,
    params=original_command.params,
    epilog=original_command.epilog,
    short_help=original_command.short_help,
    add_help_option=original_command.add_help_option,
)
@click.pass_context
def innit(ctx, **kwargs):
    """Configure Flow SDK - British version of init.

    Same as 'flow init' but with more tea and crumpets.
    """
    ctx.invoke(original_command, **kwargs)


class InnitCommand:
    """Wrapper to fit the command pattern."""

    @property
    def name(self) -> str:
        return "innit"

    @property
    def help(self) -> str:
        return "British version of init"

    def get_command(self) -> click.Command:
        return innit


command = InnitCommand()
