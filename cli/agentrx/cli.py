"""AgentRx CLI entry point."""

import click
from pathlib import Path

from . import __version__
from .commands.init import init
from .commands.prompt import prompt


@click.group()
@click.version_option(version=__version__, prog_name="arx")
@click.pass_context
def cli(ctx):
    """AgentRx - AI-assisted development tools.

    Initialize projects for agent-based development workflows.
    """
    ctx.ensure_object(dict)


# Register commands
cli.add_command(init)
cli.add_command(prompt)


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
