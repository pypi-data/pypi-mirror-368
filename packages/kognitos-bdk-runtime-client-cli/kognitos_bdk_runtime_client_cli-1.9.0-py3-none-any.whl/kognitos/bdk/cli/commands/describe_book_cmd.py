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
def describe_book(
    ctx: typer.Context,
    *,
    book_name: Optional[str] = None,
    book_version: Optional[str] = None,
    columns: Annotated[
        Optional[List[str]],
        typer.Option(help="Specify the fields to display. To select multiple fields, use this option for each field individually (e.g., --columns name --columns version)."),
    ] = None,
) -> Tuple[Any, RenderableType]:
    """Shows specific information about a book"""
    book = _resolve_book(ctx.obj.client, ctx.obj.vars, book_name, book_version)
    command_cfg = config_loader.get_command_config(
        command_name="describe_book", config_data=ctx.obj.loaded_config, cli_columns=columns, cli_column_styles=ctx.obj.cli_column_styles
    )
    return book, ui.describe.build_book_description(book, visible_fields=command_cfg["columns"])
