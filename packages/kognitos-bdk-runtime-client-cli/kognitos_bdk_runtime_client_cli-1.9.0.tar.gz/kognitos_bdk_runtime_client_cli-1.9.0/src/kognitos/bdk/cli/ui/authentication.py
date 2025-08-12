from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from rich import box
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kognitos.bdk.runtime.client.book_authentication_descriptor import (
    BookAuthenticationDescriptor, BookCustomAuthenticationDescriptor,
    BookOAuthAuthenticationDescriptor, OauthFlow)
from kognitos.bdk.runtime.client.credential_descriptor import (
    CredentialDescriptor, CredentialType)

from . import common
from . import format as fmt
from .rich_table_utils import build_detail_view, build_dynamic_table

console = Console()


def _get_auth_method_canonical_type_string(auth_method: Any) -> str:
    if isinstance(auth_method, BookCustomAuthenticationDescriptor):
        return "CUSTOM"
    if isinstance(auth_method, BookOAuthAuthenticationDescriptor):
        if hasattr(auth_method, "flows") and auth_method.flows:
            if OauthFlow.OAUTH_FLOW_CLIENT_CREDENTIALS in auth_method.flows:
                return "OAUTH2_CLIENT_CREDENTIALS"
            if OauthFlow.OAUTH_FLOW_AUTHORIZATION_CODE in auth_method.flows:
                return "OAUTH2_AUTHORIZATION_CODE"
    return "UNKNOWN"


class NoAuthenticationSentinel:
    id = "__NO_AUTH__"
    description = "Proceed without authentication"


NO_AUTH_SENTINEL = NoAuthenticationSentinel()


def _prompt_auth(
    authentications: List[BookAuthenticationDescriptor], authentication_id: Optional[str], config_vars: Optional[dict], allow_skip: bool = False
) -> Union[BookAuthenticationDescriptor, NoAuthenticationSentinel]:
    selected_authentication = None
    auth_id_to_use = common.get_from_context_or_prompt("authentication_id", authentication_id, context=config_vars, prompt_user=False)

    choices: List[Union[BookAuthenticationDescriptor, NoAuthenticationSentinel]] = list(authentications)
    if allow_skip:
        choices.insert(0, NO_AUTH_SENTINEL)

    if auth_id_to_use:
        if auth_id_to_use == NO_AUTH_SENTINEL.id and allow_skip:
            return NO_AUTH_SENTINEL
        selected_authentication = next(filter(lambda a: a.id == auth_id_to_use, choices), None)

    if not selected_authentication:
        selected_authentication = common.bdkctl_choose(
            prompt="Select Authentication",
            choices=choices,
            format_function=lambda a: (
                "No Authentication" if isinstance(a, NoAuthenticationSentinel) else f"{a.id} {f'({a.description})' if getattr(a, 'description', None) else ''}"
            ),
        )
    return selected_authentication


def _prompt_credential(credential: CredentialDescriptor, config_vars: Optional[dict]) -> Tuple[str, str]:
    value = common.get_from_context_or_prompt(credential.label, context=config_vars, var_info=credential.description, prompt_user=True)
    return credential.id, value


def _prompt_credentials(authentication: BookAuthenticationDescriptor, config_vars: Optional[dict]) -> List[Tuple[str, Any]]:
    if not hasattr(authentication, "credentials") or not isinstance(authentication.credentials, list):
        console.print(f"[yellow]Warning: Authentication '{authentication.id}' has no valid credentials list to prompt for.[/yellow]")
        return []
    credentials = list(map(lambda c: _prompt_credential(c, config_vars), authentication.credentials))
    return credentials


def prompt_authentications(
    authentications: List[BookAuthenticationDescriptor], authentication_id: Optional[str], config_vars: Optional[Dict], allow_skip: bool = False
) -> Optional[Tuple[Optional[str], Optional[List[Tuple[str, Any]]]]]:
    selected_authentication = _prompt_auth(authentications, authentication_id, config_vars, allow_skip=allow_skip)

    if selected_authentication == NO_AUTH_SENTINEL:
        return None

    if not isinstance(selected_authentication, BookAuthenticationDescriptor):
        console.print(f"[yellow]Warning: Unexpected authentication selection result: {selected_authentication}[/yellow]")
        return None

    creds_to_prompt = []
    if isinstance(selected_authentication, BookCustomAuthenticationDescriptor):
        creds_to_prompt = _prompt_credentials(selected_authentication, config_vars)
    elif selected_authentication:
        console.print(f"[dim]Selected authentication '{selected_authentication.id}' (type: {type(selected_authentication).__name__}). Credential prompting handled by flow.[/dim]")

    return selected_authentication.id, creds_to_prompt


def _build_custom_authentication_description(authentication: BookCustomAuthenticationDescriptor):
    s = f"""{fmt.format_authentication_title(authentication)}
{authentication.description}
"""
    return s


DEFAULT_AUTHENTICATION_COLUMNS = ["id", "description"]

AUTH_FIELD_ACCESSORS: Dict[str, Callable[[Any], str]] = {
    "description": lambda auth_method: str(getattr(auth_method, "description", "N/A")),
}

AUTH_DETAIL_FIELD_ACCESSORS: Dict[str, Callable[[Any], str]] = {
    "id": lambda auth: str(getattr(auth, "id", "N/A")),
    "description": lambda auth: str(getattr(auth, "description", "N/A")),
    "type": _get_auth_method_canonical_type_string,
}

DEFAULT_CREDENTIAL_COLUMNS = ["Label", "Description", "Type", "Optional"]

CREDENTIAL_FIELD_ACCESSORS: Dict[str, Callable[[Any], str]] = {
    "Label": lambda cred: str(getattr(cred, "label", "N/A")),
    "Description": lambda cred: str(getattr(cred, "description", "N/A")),
    "Type": lambda cred: (str(fmt.format_credential_type(cred_type)) if isinstance(cred_type := getattr(cred, "type", "N/A"), CredentialType) else "N/A"),
    "Optional": lambda cred: str(getattr(cred, "optional", False)),
}


def build_authentications(book: Any, visible_columns: Optional[List[str]] = None, _column_styles: Optional[Dict[str, Any]] = None) -> Table:
    """Builds a Rich Table to display available authentication methods for a book using the dynamic table utility."""
    auth_methods = getattr(book, "authentications", [])

    book_primary_name = getattr(book, "display_name", getattr(book, "name", "N/A"))
    book_version_str = getattr(book, "version", "N/A")

    table_title = f"Authentication Methods for {book_primary_name} v{book_version_str}"
    if hasattr(book, "display_name") and getattr(book, "display_name") != getattr(book, "name") and hasattr(book, "name"):
        table_title = f"Authentication Methods for {getattr(book, 'display_name')} ({getattr(book, 'name')} v{book_version_str})"

    no_items_msg = f"No authentication methods found for {book_primary_name} v{book_version_str}."

    return build_dynamic_table(
        items=auth_methods,
        default_columns=DEFAULT_AUTHENTICATION_COLUMNS,
        field_accessors=AUTH_FIELD_ACCESSORS,
        visible_columns=visible_columns,
        column_styles=_column_styles,
        table_title=table_title,
        no_items_message=no_items_msg,
        get_item_id_for_error=lambda auth: getattr(auth, "id", "Unknown Auth ID"),
    )


def _build_custom_authentication_details(
    authentication_param: BookCustomAuthenticationDescriptor,
    _book_name: str,
    _book_version: str,
    custom_auth_columns: Optional[List[str]] = None,
    column_styles: Optional[Dict[str, Any]] = None,
) -> Optional[Table]:
    """Builds a table for custom authentication credentials using build_dynamic_table."""

    if not hasattr(authentication_param, "credentials") or not authentication_param.credentials:
        return None

    credentials_list = authentication_param.credentials

    return build_dynamic_table(
        items=credentials_list,
        default_columns=DEFAULT_CREDENTIAL_COLUMNS,
        field_accessors=CREDENTIAL_FIELD_ACCESSORS,
        visible_columns=custom_auth_columns,
        column_styles=column_styles,
        table_title=None,
        no_items_message="This custom authentication method does not define any credentials.",
        get_item_id_for_error=lambda cred: getattr(cred, "label", "Unknown Credential"),
    )


def _build_oauth_authentication_details(
    authentication: BookOAuthAuthenticationDescriptor, book_name: str, book_version: str, _column_styles: Optional[Dict[str, Any]] = None
) -> RenderableType:
    header = f"[bold]Authentication Details for '{authentication.id}'[/bold]\nBook: {book_name} v{book_version}\nType: OAuth"
    provider = fmt.format_oauth_provider(authentication.provider)
    flows = ", ".join([fmt.format_oauth_flow(flow) for flow in authentication.flows])

    content = (
        f"{header}\n"
        f"Description: {getattr(authentication, 'description', 'N/A')}\n"
        f"Provider: {provider}\n"
        f"Flows: {flows}\n"
        f"Authorize Endpoint: {authentication.authorize_endpoint}\n"
        f"Token Endpoint: {authentication.token_endpoint}"
    )
    if authentication.scopes:
        content += f"\nScopes: {', '.join(authentication.scopes)}"
    return content


def build_authentication_description(
    auth_method: Any,
    book_name: str,
    book_version: str,
    custom_auth_columns: Optional[List[str]] = None,
    column_styles: Optional[Dict[str, Any]] = None,
) -> RenderableType:
    """Builds a Rich Renderable to display detailed information about an authentication method, wrapped in Panels."""
    if not auth_method:
        return Panel(Text("Authentication method details not available.", style="red"), title="[bold red]Error[/bold red]")

    _column_styles = column_styles or {}
    output_elements: List[RenderableType] = []

    auth_id_for_title = AUTH_DETAIL_FIELD_ACCESSORS.get("id", lambda am: "N/A")(auth_method)
    basic_info_table = build_detail_view(
        item=auth_method,
        fields_to_display=["id", "description", "type"],
        field_accessors=AUTH_DETAIL_FIELD_ACCESSORS,
        table_title=None,
        column_styles=_column_styles.get("basic", _column_styles),
    )
    if basic_info_table.rows:
        output_elements.append(
            Panel(basic_info_table, title=f"[bold steel_blue]Authentication Overview: {auth_id_for_title}[/bold steel_blue]", border_style="green", expand=False)
        )

    auth_type_value = AUTH_DETAIL_FIELD_ACCESSORS.get("type", lambda am: "UNKNOWN")(auth_method)
    specific_details_elements: List[RenderableType] = []
    specific_details_panel_title = ""

    if auth_type_value in ("OAUTH2_CLIENT_CREDENTIALS", "OAUTH2_AUTHORIZATION_CODE"):
        specific_details_panel_title = "[bold cyan]OAuth Configuration[/bold cyan]"
        oauth_table = Table(show_header=False, box=box.MINIMAL, padding=(0, 1))
        oauth_table.add_column("Field", style="bold green")
        oauth_table.add_column("Value")
        oauth_fields = ["token_url", "authorization_url", "scopes", "client_id_concept_id", "client_secret_concept_id"]
        for field in oauth_fields:
            if hasattr(auth_method, field):
                val = getattr(auth_method, field, "N/A")
                if isinstance(val, list):
                    val = ", ".join(map(str, val)) if val else "N/A"
                value_style_key = f"oauth.{field}"
                style = _column_styles.get(value_style_key, _column_styles.get(field, {}))
                value_s = style.get("value") if isinstance(style, dict) else style if isinstance(style, str) else ""
                oauth_table.add_row(field.replace("_", " ").capitalize(), str(val), style=value_s if value_s else None)
        if oauth_table.rows:
            specific_details_elements.append(oauth_table)
        else:
            specific_details_elements.append(Text("No specific OAuth details configured.", style="dim"))

    elif auth_type_value == "CUSTOM" and hasattr(auth_method, "credentials"):
        specific_details_panel_title = "[bold cyan]Custom Credentials[/bold cyan]"
        cred_table = _build_custom_authentication_details(auth_method, book_name, book_version, custom_auth_columns, column_styles)
        if cred_table:
            specific_details_elements.append(cred_table)
        else:
            specific_details_elements.append(Text("This custom authentication method does not define any credentials.", style="dim"))

    if specific_details_elements:
        output_elements.append(Panel(Group(*specific_details_elements), title=specific_details_panel_title, border_style="blue", expand=False))

    if not output_elements:
        return Panel(Text(f"No details to display for authentication method ID: {auth_id_for_title}", style="yellow"), title="[bold yellow]Information[/bold yellow]")

    return Group(*output_elements)


def prompt_credentials(auth_method: BookAuthenticationDescriptor, context_vars: Dict[str, Any], *, _prompt_optional: bool = False) -> Dict[str, Any]:
    credentials_dict = {}
    if isinstance(auth_method, BookCustomAuthenticationDescriptor):
        if not auth_method.credentials:
            return {}

        for cred_desc in auth_method.credentials:
            value = common.get_from_context_or_prompt(var_name=cred_desc.label, value=None, context=context_vars, var_info=cred_desc.description, prompt_user=True)
            credentials_dict[cred_desc.id] = value
    return credentials_dict
