from typing import Any, Callable, Dict, List, Optional

from rich.table import Table

from .rich_table_utils import build_dynamic_table

DEFAULT_COLUMNS = ["name", "display_name", "version", "short_description", "connection_required"]

FIELD_ACCESSORS: Dict[str, Callable[[Any], str]] = {
    "signature": lambda book: str(getattr(getattr(book, "signature", None), "english", "N/A")),
    "connection_required": lambda book: str(getattr(book, "connection_required", "N/A")),
}


def build_books(books: List[Any], visible_columns: Optional[List[str]] = None, column_styles: Optional[Dict[str, Any]] = None) -> Table:
    """Builds a Rich Table to display a list of books."""

    table_title = "Available Books"
    no_items_msg = "No books found."

    return build_dynamic_table(
        items=books,
        default_columns=DEFAULT_COLUMNS,
        field_accessors=FIELD_ACCESSORS,
        visible_columns=visible_columns,
        column_styles=column_styles,
        table_title=table_title,
        no_items_message=no_items_msg,
    )
