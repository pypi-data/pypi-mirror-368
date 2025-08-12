from typing import Any, Callable, Dict, List, Optional

from rich.table import Table

from kognitos.bdk.runtime.client.concept_descriptor import ConceptDescriptor

from . import format as fmt
from .rich_table_utils import build_dynamic_table

DEFAULT_CONFIG_COLUMNS = ["name", "type", "description"]

CONFIG_ITEM_FIELD_ACCESSORS: Dict[str, Callable[[Any], str]] = {
    "name": lambda item: str(getattr(getattr(item, "concept", item), "name", "N/A")),
    "type": lambda item: str(
        getattr(
            getattr(getattr(item, "concept", item), "type", None),
            "name",
            getattr(getattr(item, "concept", item), "type", "N/A"),
        )
    ),
    "description": lambda item: str(getattr(getattr(item, "concept", item), "description", "N/A")),
    "value": lambda item: str(getattr(item, "value", "N/A")),
}


def _build_book_config(table: Table, config: ConceptDescriptor, columns_to_display: List[str]):
    row_data = []
    for col in columns_to_display:
        if col == "concept":
            if config.noun_phrases and config.noun_phrases.noun_phrases:
                row_data.append(fmt.format_noun_phrase(config.noun_phrases.noun_phrases[0]))
            else:
                row_data.append("N/A")
        elif col == "type":
            row_data.append(f"[bold encircle]{fmt.format_concept_type(config.type)}[/]")
        elif col == "description":
            row_data.append(config.description)
    if row_data:
        table.add_row(*row_data)


def build_book_configs(book: Any, visible_columns: Optional[List[str]] = None, column_styles: Optional[Dict[str, Any]] = None) -> Table:
    """Builds a Rich Table to display configurations for a book."""
    configs_to_display = getattr(book, "configurations", [])

    book_primary_name = getattr(book, "display_name", getattr(book, "name", "N/A"))
    book_version_str = getattr(book, "version", "N/A")

    table_title = f"Configurations for {book_primary_name} v{book_version_str}"
    if hasattr(book, "display_name") and getattr(book, "display_name") != getattr(book, "name") and hasattr(book, "name"):
        table_title = f"Configurations for {getattr(book, 'display_name')} ({getattr(book, 'name')} v{book_version_str})"

    no_items_msg = f"No configurations found for {book_primary_name} v{book_version_str}."

    return build_dynamic_table(
        items=configs_to_display,
        default_columns=DEFAULT_CONFIG_COLUMNS,
        field_accessors=CONFIG_ITEM_FIELD_ACCESSORS,
        visible_columns=visible_columns,
        column_styles=column_styles,
        table_title=table_title,
        no_items_message=no_items_msg,
        get_item_id_for_error=lambda item: str(getattr(getattr(item, "concept", item), "id", "Unknown Config ID")),
    )
