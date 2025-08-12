import logging
from typing import Annotated, Any, List, Optional, Tuple

import typer
from rich.console import Console, RenderableType

from kognitos.bdk.cli import ui
from kognitos.bdk.cli.config import config_loader
from kognitos.bdk.cli.core.client import BDKClient
from kognitos.bdk.cli.utils import handle_output

console = Console()
logger = logging.getLogger("bdkctl")


@handle_output
def describe_books(
    ctx: typer.Context,
    *,
    columns: Annotated[
        Optional[List[str]],
        typer.Option(help="Specify the columns to display. To select multiple columns, use this option for each column individually (e.g., --columns name --columns version)."),
    ] = None,
) -> Tuple[Any, RenderableType]:
    """Lists basic information about books"""
    client: BDKClient = ctx.obj.client
    command_cfg = config_loader.get_command_config(
        command_name="describe_books", config_data=ctx.obj.loaded_config, cli_columns=columns, cli_column_styles=ctx.obj.cli_column_styles
    )
    retrieved_books = client.retrieve_books()
    return retrieved_books, ui.books.build_books(retrieved_books, visible_columns=command_cfg["columns"], column_styles=command_cfg["column_styles"])
