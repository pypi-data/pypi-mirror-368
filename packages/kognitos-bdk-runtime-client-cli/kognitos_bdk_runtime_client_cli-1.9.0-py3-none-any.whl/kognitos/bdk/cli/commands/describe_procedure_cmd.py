import logging
from typing import Annotated, Any, List, Optional, Tuple

import typer
from rich.console import Console, RenderableType

from kognitos.bdk.cli import ui
from kognitos.bdk.cli.config import config_loader
from kognitos.bdk.cli.core.client import BDKClient
from kognitos.bdk.cli.utils import (_resolve_book,
                                    get_client_with_endpoint_or_state_client,
                                    handle_output)

console = Console()
logger = logging.getLogger("bdkctl")


@handle_output
def describe_procedure(
    ctx: typer.Context,
    *,
    book_name: Optional[str] = None,
    book_version: Optional[str] = None,
    procedure_id: Optional[str] = None,
    include_connect: bool = False,
    columns: Annotated[
        Optional[List[str]],
        typer.Option(
            help="Specify the columns to display for input and output tables. To select multiple columns, use this option for each column individually (e.g., --columns Concept --columns Type)."
        ),
    ] = None,
) -> Tuple[Any, RenderableType]:
    """Describes a procedure for a given book"""
    book = _resolve_book(ctx.obj.client, ctx.obj.vars, book_name=book_name, book_version=book_version)
    client: BDKClient = get_client_with_endpoint_or_state_client(ctx.obj.client, book)
    command_cfg = config_loader.get_command_config(
        command_name="describe_procedure", config_data=ctx.obj.loaded_config, cli_columns=columns, cli_column_styles=ctx.obj.cli_column_styles
    )

    procedure_to_describe = None
    if procedure_id:
        procedure_to_describe = client.retrieve_procedure(name=book.name, version=book.version, procedure_id=procedure_id, include_connect=include_connect)
        if not procedure_to_describe:
            console.print(f"[red bold]Error:[/red bold] Procedure with ID '[b]{procedure_id}[/b]' not found in book '[b]{book.name} v{book.version}[/b]'.")
            raise typer.Exit(code=1)
    else:
        all_procedures = client.retrieve_procedures(name=book.name, version=book.version, include_connect=include_connect)
        if not all_procedures:
            console.print(f"[yellow]No procedures found for book '[b]{book.name} v{book.version}[/b]'.[/yellow]")
            return None, ""
        procedure_to_describe = ui.common.bdkctl_choose("Choose a procedure to describe", all_procedures, lambda p: p.id)
        if not procedure_to_describe:
            console.print("[yellow]No procedure selected.[/yellow]")
            raise typer.Exit(code=1)

    return procedure_to_describe, ui.procedure.build_procedure(
        procedure_to_describe,
        input_columns=(command_cfg.get("columns") or {}).get("inputs"),
        output_columns=(command_cfg.get("columns") or {}).get("outputs"),
        column_styles=command_cfg.get("column_styles", {}),
    )
