from typing import Any, Callable, Dict, List, Optional

from rich import box
from rich.table import Table
from rich.text import Text


def _log_error(message: str):
    print(f"[Error] {message}")


def _get_field_value_as_string(item: Any, field_name: str, field_accessors: Dict[str, Callable[[Any], str]], get_item_id_for_error: Optional[Callable[[Any], str]] = None) -> str:
    """
    Internal helper to get a field's value as a string, using accessors or getattr.
    Handles errors and ensures the output is a string.
    """
    value_str = "N/A"
    try:
        if field_name in field_accessors:
            value_str = field_accessors[field_name](item)
        else:
            raw_value = getattr(item, field_name, "N/A")
            value_str = str(raw_value)
    except AttributeError:
        item_id_str = ""
        if get_item_id_for_error and item is not None:
            try:
                item_id_val = get_item_id_for_error(item)
                if item_id_val is not None:
                    item_id_str = f" for item '{item_id_val}'"
            except Exception:
                pass
        _log_error(f"Attribute error for field '{field_name}'{item_id_str}")
        value_str = "Attribute Error!"
    except ValueError as ve:
        item_id_str = ""
        if get_item_id_for_error and item is not None:
            try:
                item_id_val = get_item_id_for_error(item)
                if item_id_val is not None:
                    item_id_str = f" for item '{item_id_val}'"
            except Exception:
                pass
        _log_error(f"Value error for field '{field_name}'{item_id_str}: {ve}")
        value_str = "Value Error!"
    except Exception as e:
        item_id_str = ""
        if get_item_id_for_error and item is not None:
            try:
                item_id_val = get_item_id_for_error(item)
                if item_id_val is not None:
                    item_id_str = f" for item '{item_id_val}'"
            except Exception:
                pass
        _log_error(f"Accessor or processing error for field '{field_name}'{item_id_str}: {e}")
        value_str = "Processing Error!"

    return str(value_str) if value_str is not None else "N/A"


def build_dynamic_table(
    items: List[Any],
    default_columns: List[str],
    field_accessors: Dict[str, Callable[[Any], str]],
    visible_columns: Optional[List[str]] = None,
    column_styles: Optional[Dict[str, Any]] = None,
    table_title: Optional[str] = None,
    no_items_message: str = "No items found.",
    get_item_id_for_error: Optional[Callable[[Any], str]] = None,
) -> Table:
    """
    Builds a Rich Table dynamically based on the provided configurations.

    Args:
        items: The list of items (objects) to display.
        default_columns: Default columns to display if visible_columns is not provided.
        field_accessors: A dictionary mapping column names to functions that extract/format the field value from an item.
        visible_columns: Specific columns to display, overrides default_columns.
        column_styles: Rich styles for columns (header and justify).
        table_title: Optional title for the table.
        no_items_message: Message to display if the items list is empty.
        get_item_id_for_error: Optional function to get a unique ID from an item for error logging.
    Returns:
        A Rich Table object.
    """
    _column_styles = column_styles or {}
    columns_to_display = visible_columns or default_columns

    table = Table(box=box.SIMPLE, padding=(0, 1))
    if table_title:
        table.title = table_title

    if not items:
        if not columns_to_display:
            table.add_column("Info")
            table.add_row(Text(no_items_message, justify="center"))
        else:
            for col_name in columns_to_display:
                header_display = "ID" if col_name == "id" else col_name.replace("_", " ").capitalize()
                style_info = _column_styles.get(col_name, {})
                if not isinstance(style_info, dict):
                    style_info = {"header": style_info, "justify": "left"}
                table.add_column(header_display, style=style_info.get("header"), justify=style_info.get("justify", "left"))
            if len(columns_to_display) == 1:
                table.add_row(Text(no_items_message, justify="center"))
            elif columns_to_display:
                row_data = [Text(no_items_message, justify="center")] + ["" for _ in range(len(columns_to_display) - 1)]
                table.add_row(*row_data)
        return table

    for col_name in columns_to_display:
        header_display = "ID" if col_name == "id" else col_name.replace("_", " ").capitalize()
        style_info = _column_styles.get(col_name, {})
        if not isinstance(style_info, dict):
            style_info = {"header": style_info, "justify": "left"}
        table.add_column(header_display, style=style_info.get("header"), justify=style_info.get("justify", "left"))

    for item in items:
        row_data = []
        for col_name in columns_to_display:
            cell_value = _get_field_value_as_string(item, col_name, field_accessors, get_item_id_for_error)
            row_data.append(cell_value)
        table.add_row(*row_data)
    return table


def build_detail_view(
    item: Any,
    fields_to_display: List[str],
    field_accessors: Dict[str, Callable[[Any], str]],
    table_title: Optional[str] = None,
    column_styles: Optional[Dict[str, Any]] = None,
    key_column_name: str = "Field",
    value_column_name: str = "Value",
    key_column_style: Optional[str] = "bold cyan",
) -> Table:
    """
    Builds a Rich Table for a key-value detail view of a single item.

    Args:
        item: The item (object) to display details for.
        fields_to_display: A list of field names to show.
        field_accessors: Dictionary mapping field names to functions that extract/format the value.
        table_title: Optional title for the table.
        column_styles: Styles for the values of specific fields (e.g., {"field_name": "bold red"}).
        key_column_name: Name for the key/field column.
        value_column_name: Name for the value column.
        key_column_style: Style for the displayed keys/field names in the first column.
    Returns:
        A Rich Table object.
    """
    _column_styles = column_styles or {}

    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    if table_title:
        table.title = table_title

    table.add_column(key_column_name, style=key_column_style)
    table.add_column(value_column_name)

    if item is None:
        table.add_row(key_column_name, "Error: Item data not available.")
        return table

    for field_name in fields_to_display:
        field_display_name = "ID" if field_name == "id" else field_name.replace("_", " ").capitalize()

        value_str = _get_field_value_as_string(item, field_name, field_accessors, get_item_id_for_error=lambda i: str(getattr(i, "id", "current item")))

        value_style_info = _column_styles.get(field_name, {})
        actual_value_style = value_style_info.get("value") if isinstance(value_style_info, dict) else value_style_info if isinstance(value_style_info, str) else ""

        table.add_row(field_display_name, value_str, style=actual_value_style if actual_value_style else None)

    return table
