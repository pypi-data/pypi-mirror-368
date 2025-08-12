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
def describe_authentications(
    ctx: typer.Context,
    *,
    book_name: Optional[str] = None,
    book_version: Optional[str] = None,
    columns: Annotated[
        Optional[List[str]],
        typer.Option(
            help="Specify the columns to display (e.g., id, description, type). To select multiple columns, use this option for each column individually (e.g., --columns id --columns type)."
        ),
    ] = None,
) -> Tuple[Any, RenderableType]:
    """Shows all authentication methods available for a given book"""
    book = _resolve_book(ctx.obj.client, ctx.obj.vars, book_name=book_name, book_version=book_version)
    command_cfg = config_loader.get_command_config(
        command_name="describe_authentications", config_data=ctx.obj.loaded_config, cli_columns=columns, cli_column_styles=ctx.obj.cli_column_styles
    )
    return book.authentications, ui.authentication.build_authentications(book, visible_columns=command_cfg["columns"], _column_styles=command_cfg["column_styles"])
