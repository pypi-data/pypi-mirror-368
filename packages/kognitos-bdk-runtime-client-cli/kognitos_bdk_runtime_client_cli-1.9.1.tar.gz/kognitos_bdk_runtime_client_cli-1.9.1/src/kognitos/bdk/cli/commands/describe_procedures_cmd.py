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
def describe_procedures(
    ctx: typer.Context,
    *,
    book_name: Optional[str] = None,
    book_version: Optional[str] = None,
    include_connect: bool = False,
    columns: Annotated[
        Optional[List[str]],
        typer.Option(help="Specify the columns to display. To select multiple columns, use this option for each column individually (e.g., --columns id --columns signature)."),
    ] = None,
) -> Tuple[Any, RenderableType]:
    """Displays procedures for a given book"""
    book = _resolve_book(ctx.obj.client, ctx.obj.vars, book_name=book_name, book_version=book_version)
    client: BDKClient = get_client_with_endpoint_or_state_client(ctx.obj.client, book)
    command_cfg = config_loader.get_command_config(
        command_name="describe_procedures", config_data=ctx.obj.loaded_config, cli_columns=columns, cli_column_styles=ctx.obj.cli_column_styles
    )
    book_procedures = client.retrieve_procedures(name=book.name, version=book.version, include_connect=include_connect)
    return book_procedures, ui.procedure.build_procedures(book_procedures, visible_columns=command_cfg["columns"], column_styles=command_cfg["column_styles"])
