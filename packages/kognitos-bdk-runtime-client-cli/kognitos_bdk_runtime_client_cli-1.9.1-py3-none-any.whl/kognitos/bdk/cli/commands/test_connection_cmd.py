import logging
from typing import Any, List, Optional, Tuple

import typer
from rich.console import Console, RenderableType

from kognitos.bdk.cli.core.client import BDKClient
from kognitos.bdk.cli.ui.authentication import (AUTH_DETAIL_FIELD_ACCESSORS,
                                                prompt_authentications)
from kognitos.bdk.cli.ui.common import (build_simple_message,
                                        get_from_context_or_prompt)
from kognitos.bdk.cli.utils import (_resolve_book,
                                    get_client_with_endpoint_or_state_client,
                                    handle_output)
from kognitos.bdk.runtime.client.exceptions import BDKRuntimeClientError

console = Console()
logger = logging.getLogger("bdkctl")


@handle_output
def test_connection(
    ctx: typer.Context, *, book_name: Optional[str] = None, book_version: Optional[str] = None, authentication_id: Optional[str] = None
) -> Tuple[Any, RenderableType]:
    """Tests connection to a book's endpoint, optionally using an authentication method."""
    client: BDKClient = ctx.obj.client
    book = _resolve_book(client, ctx.obj.vars, book_name=book_name, book_version=book_version)
    test_client: BDKClient = get_client_with_endpoint_or_state_client(client, book)

    auth_id_to_use: Optional[str] = None
    credentials_to_use: Optional[List[Tuple[str, Any]]] = None

    pre_selected_auth_id = get_from_context_or_prompt("authentication_id", authentication_id, context=ctx.obj.vars, prompt_user=False)

    if pre_selected_auth_id:
        auth_id_to_use = pre_selected_auth_id
        selected_auth_method = next((auth for auth in book.authentications if auth.id == auth_id_to_use), None)
        if selected_auth_method and AUTH_DETAIL_FIELD_ACCESSORS["type"](selected_auth_method) == "CUSTOM":
            pass

    else:
        if book.authentications:
            connection_is_required = getattr(book, "connection_required", False)

            auth_selection_result = prompt_authentications(
                authentications=book.authentications, authentication_id=None, config_vars=ctx.obj.vars, allow_skip=(not connection_is_required)
            )
            if auth_selection_result:
                auth_id_to_use, credentials_to_use = auth_selection_result
            elif connection_is_required:
                console.print("[red bold]Error: This book requires authentication, but none was selected.[/red bold]")
                raise typer.Exit(code=1)
        elif getattr(book, "connection_required", False):
            console.print("[red bold]Error: This book requires authentication, but no authentication methods are defined for it.[/red bold]")
            raise typer.Exit(code=1)
        else:
            console.print("[yellow]No authentication methods defined for this book. Proceeding without authentication.[/yellow]")

    try:
        test_client.test_connection(name=book.name, version=book.version, authentication_id=auth_id_to_use, authentication_credentials=credentials_to_use)
        success = True
        message = "Connection successful."
        logger.info("Connection test successful for book %s v%s (auth: %s)", book.name, book.version, auth_id_to_use)
        raw_output = {"book": book.name, "version": book.version, "authentication_id": auth_id_to_use, "success": success, "message": message}
        return raw_output, build_simple_message(message, success=success)
    except BDKRuntimeClientError as e:
        logger.error("Connection test failed for book %s v%s (auth: %s): %s", book.name, book.version, auth_id_to_use, e, exc_info=True)
        err_msg = f"Connection test failed: {e.message if hasattr(e, 'message') else e}"
        raw_output = {"book": book.name, "version": book.version, "authentication_id": auth_id_to_use, "success": False, "message": err_msg}
        return raw_output, build_simple_message(err_msg, success=False)
    except Exception as e:
        logger.error("Connection test failed with an unexpected error for book %s v%s (auth: %s): %s", book.name, book.version, auth_id_to_use, e, exc_info=True)
        err_msg = f"Connection test failed with an unexpected error: {e}"
        raw_output = {"book": book.name, "version": book.version, "authentication_id": auth_id_to_use, "success": False, "message": err_msg}
        return raw_output, build_simple_message(err_msg, success=False)
