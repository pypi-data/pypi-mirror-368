from typing import Annotated, Optional

import typer
from rich.console import Console

console = Console()


def custom_help(
    ctx: typer.Context,
    command_name: Annotated[
        Optional[str],
        typer.Argument(
            metavar="COMMAND_NAME",
            help="The command to get help for. If not provided, shows general help for the application.",
        ),
    ] = None,
):
    """Shows help for bdkctl commands or a specific command."""
    if not ctx.parent or not ctx.parent.command:
        console.print("[red bold]Error:[/red bold] Cannot display help, invalid context.")
        raise typer.Exit(code=1)

    if command_name:
        command_obj = ctx.parent.command.commands.get(command_name)
        if command_obj:
            console.print(command_obj.get_help(ctx.parent))
        else:
            console.print(f"[red bold]Error:[/red bold] Unknown command '[b]{command_name}[/b]'.")
            console.print("\nAvailable commands are:")
            if ctx.parent.command.commands:
                cmd_items = sorted(ctx.parent.command.commands.items())
                max_len = 0
                if cmd_items:
                    max_len = max(len(name) for name, cmd_info_val in cmd_items if not cmd_info_val.hidden)
                for name, cmd_info_val in cmd_items:
                    if not cmd_info_val.hidden:
                        help_text = cmd_info_val.get_short_help_str()
                        console.print(f"  [b]{name.ljust(max_len)}[/b]  {help_text}")
            else:
                console.print("  No commands available.")
            console.print(f"\nRun '[b]{ctx.parent.info_name} help[/b]' for general help or '[b]{ctx.parent.info_name} help [COMMAND_NAME][/b]' for command-specific help.")
            raise typer.Exit(code=1)
    else:
        console.print(ctx.parent.get_help())
