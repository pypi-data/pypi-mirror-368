import logging
from typing import Annotated, Any, List, Optional, Tuple

import typer
from rich.console import Console, RenderableType

from kognitos.bdk.cli import ui
from kognitos.bdk.cli.core.client import BDKClient
from kognitos.bdk.cli.utils import _resolve_book, handle_output

console = Console()
logger = logging.getLogger("bdkctl")


@handle_output
def describe_configurations(
    ctx: typer.Context,
    *,
    book_name: Optional[str] = None,
    book_version: Optional[str] = None,
    columns: Annotated[
        Optional[List[str]],
        typer.Option(help="Specify the columns to display. To select multiple columns, use this option for each column individually (e.g., --columns name --columns id)."),
    ] = None,
) -> Tuple[Any, RenderableType]:
    """Displays configurations for a given book"""
    client: BDKClient = ctx.obj.client
    book = _resolve_book(client, ctx.obj.vars, book_name=book_name, book_version=book_version)

    renderable_output = ui.build_book_configs(book=book, visible_columns=columns, column_styles=ctx.obj.cli_column_styles.get("configurations", ctx.obj.cli_column_styles))
    raw_data = {"book_name": book.name, "book_version": book.version, "configurations": getattr(book, "configurations", [])}
    return raw_data, renderable_output
