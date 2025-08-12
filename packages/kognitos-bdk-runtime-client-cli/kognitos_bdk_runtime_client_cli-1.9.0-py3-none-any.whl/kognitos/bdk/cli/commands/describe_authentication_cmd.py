import logging
from typing import Annotated, Any, List, Optional, Tuple

import typer
from rich.console import Console, RenderableType

from kognitos.bdk.cli import ui
from kognitos.bdk.cli.config import config_loader
from kognitos.bdk.cli.utils import _resolve_book, handle_output

console = Console()
logger = logging.getLogger("bdkctl")


@handle_output
def describe_authentication(
    ctx: typer.Context,
    *,
    book_name: Optional[str] = None,
    book_version: Optional[str] = None,
    authentication_id: Optional[str] = None,
    columns: Annotated[
        Optional[List[str]],
        typer.Option(
            help="Specify columns for the credentials table (if custom auth). To select multiple columns, use this option for each column individually (e.g., --columns Label --columns Type)."
        ),
    ] = None,
) -> Tuple[Any, RenderableType]:
    """Shows details for a specific authentication method"""
    book = _resolve_book(ctx.obj.client, ctx.obj.vars, book_name=book_name, book_version=book_version)

    auth_method_to_describe = None
    if authentication_id:
        auth_method_to_describe = next((auth for auth in book.authentications if auth.id == authentication_id), None)
        if not auth_method_to_describe:
            console.print(f"[red bold]Error:[/red bold] Authentication method with ID '[b]{authentication_id}[/b]' not found in book '[b]{book.name} v{book.version}[/b]'.")
            raise typer.Exit(code=1)
    elif book.authentications:
        auth_method_to_describe = ui.common.bdkctl_choose("Choose an authentication method", book.authentications, lambda auth: auth.id)
        if not auth_method_to_describe:
            console.print("[yellow]No authentication method selected.[/yellow]")
            raise typer.Exit(code=1)
    else:
        console.print(f"[yellow]No authentication methods found for book '[b]{book.name} v{book.version}[/b]'.[/yellow]")
        return None, ""

    command_cfg = config_loader.get_command_config(
        command_name="describe_authentication", config_data=ctx.obj.loaded_config, cli_columns=columns, cli_column_styles=ctx.obj.cli_column_styles
    )
    return auth_method_to_describe, ui.authentication.build_authentication_description(
        auth_method_to_describe, book.name, book.version, custom_auth_columns=command_cfg["columns"], column_styles=command_cfg["column_styles"]
    )
