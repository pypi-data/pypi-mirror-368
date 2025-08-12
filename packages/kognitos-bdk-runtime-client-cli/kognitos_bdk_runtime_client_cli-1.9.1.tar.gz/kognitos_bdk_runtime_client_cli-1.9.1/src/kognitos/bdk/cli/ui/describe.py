from typing import Any, Callable, Dict, List, Optional

from rich.panel import Panel
from rich.text import Text

from .rich_table_utils import _get_field_value_as_string

DEFAULT_BOOK_FIELDS = ["id", "name", "display_name", "version", "description", "author", "endpoint", "connection_required", "icon", "authentications_summary"]

BOOK_DETAIL_FIELD_ACCESSORS: Dict[str, Callable[[Any], str]] = {
    "display_name": lambda book: str(getattr(book, "display_name", getattr(book, "name", "N/A"))),
    "description": lambda book: str(getattr(book, "long_description", None) or getattr(book, "short_description", "N/A") or "N/A"),
    "connection_required": lambda book: str(bool(getattr(book, "connection_required", False))),
    "icon": lambda book: "Present" if getattr(book, "icon", None) else "Not provided",
    "authentications_summary": lambda book: f"{count} method(s) defined" if (count := len(getattr(book, "authentications", []))) > 0 else "None defined",
}


def build_book_description(book: Any, visible_fields: Optional[List[str]] = None, _column_styles: Optional[Dict[str, Any]] = None) -> Panel:
    """Builds a Rich Panel to display detailed information about a book."""

    fields_to_use = visible_fields or DEFAULT_BOOK_FIELDS

    book_name_for_title = BOOK_DETAIL_FIELD_ACCESSORS.get("display_name", lambda b: getattr(b, "name", "N/A"))(book)
    book_version_for_title = getattr(book, "version", "N/A")
    panel_title = f"Book Details: {book_name_for_title} v{book_version_for_title}"

    if book is None:
        return Panel(Text("Error: Book data not available.", style="red"), title=panel_title, border_style="red")

    content_lines = []
    for field_name in fields_to_use:
        field_display_name = "ID" if field_name == "id" else field_name.replace("_", " ").capitalize()
        value_str = _get_field_value_as_string(book, field_name, BOOK_DETAIL_FIELD_ACCESSORS, get_item_id_for_error=lambda i: str(getattr(i, "id", "current book")))
        content_lines.append(f"[bold]{field_display_name}:[/] {value_str}")

    description_text = Text.from_markup("\n".join(content_lines), justify="left")
    return Panel(description_text, title=panel_title, expand=False, border_style="blue")
