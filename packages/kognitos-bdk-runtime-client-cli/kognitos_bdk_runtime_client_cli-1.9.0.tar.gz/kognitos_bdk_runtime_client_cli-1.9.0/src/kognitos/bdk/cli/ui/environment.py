from typing import Any, Dict, Mapping, Optional

from rich import box
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kognitos.bdk.runtime.client.environment_information import \
    EnvironmentInformation

from . import common

console = Console()


def build_environment(environment_info: EnvironmentInformation):
    environment_description = f"""
[bold green]Runtime name:[/] {environment_info.runtime_name}

[bold green]Runtime Version:[/] {environment_info.runtime_version}

[bold green]BCI Protocol Version:[/] {environment_info.bci_protocol_version}

[bold green]Version:[/] {environment_info.version}

[bold green]Path:[/] \n{common.build_bdkctl_list(environment_info.path)}
"""
    return environment_description


def build_environment_display(
    cli_env_info: Dict[str, Any],
    all_endpoints: Mapping[str, Any],
    authentications_config: Mapping[str, Any],
    runtime_info: Optional[EnvironmentInformation] = None,
    runtime_info_error: Optional[str] = None,
) -> RenderableType:
    """Builds a rich display for the CLI and BDK Runtime environment information."""

    output_elements = []

    if runtime_info:
        runtime_details_str = build_environment(runtime_info)
        output_elements.append(Panel(Text.from_markup(runtime_details_str.strip()), title="[bold purple]BDK Runtime Details[/bold purple]", border_style="purple", expand=False))
    elif runtime_info_error:
        output_elements.append(Panel(Text(runtime_info_error, style="yellow"), title="[bold purple]BDK Runtime Details[/bold purple]", border_style="yellow", expand=False))

    cli_env_table = Table(show_header=False, box=None)
    cli_env_table.add_column("Key", style="bold cyan")
    cli_env_table.add_column("Value")
    for key, value in cli_env_info.items():
        if key != "endpoints":
            cli_env_table.add_row(key, str(value))

    cli_env_panel = Panel(cli_env_table, title="[bold steel_blue]BDK CLI Environment[/bold steel_blue]", border_style="green", expand=False)
    output_elements.append(cli_env_panel)

    endpoint_renderables = []
    if all_endpoints:
        for name, details in all_endpoints.items():
            endpoint_details_table = Table(show_header=False, box=box.ROUNDED, expand=True, padding=(0, 1, 0, 1))
            endpoint_details_table.add_column("Detail", style="magenta", overflow="fold")
            endpoint_details_table.add_column("Value", overflow="fold")

            endpoint_details_table.add_row("URL", details.get("url", "N/A"))
            auth_type = details.get("auth_type", "N/A")
            endpoint_details_table.add_row("Authentication Type", auth_type)

            auth_id = details.get("authentication_id")

            auth_renderable_content = []

            if auth_id:
                endpoint_details_table.add_row("Default Auth ID", Text.from_markup(f"[link={auth_id}]{auth_id}[/link]"))
                auth_config = authentications_config.get(auth_id, {})
                if auth_config:
                    auth_specific_details_table = Table(show_header=False, box=None, expand=True, padding=(0, 1, 0, 1))
                    auth_specific_details_table.add_column("Key", style="dim cyan", overflow="fold")
                    auth_specific_details_table.add_column("Value", overflow="fold")

                    auth_details_to_show = {
                        "basic": ["username"],
                        "bearer": [],
                        "oauth2_client_credentials": ["client_id", "token_url", "scopes"],
                    }.get(auth_type, [])

                    added_auth_details = False
                    for detail_key in auth_details_to_show:
                        if detail_key in auth_config:
                            val_to_show = auth_config[detail_key]
                            if isinstance(val_to_show, list):
                                val_to_show = ", ".join(val_to_show)
                            auth_specific_details_table.add_row(f"{detail_key.replace('_', ' ').title()}", str(val_to_show))
                            added_auth_details = True

                    if not added_auth_details and auth_type not in ["none", "N/A", "bearer"]:
                        auth_specific_details_table.add_row("(Details for this auth type are hidden or not configured for display)", "")

                    if added_auth_details or (not added_auth_details and auth_type not in ["none", "N/A", "bearer"]):
                        auth_renderable_content.append(
                            Panel(auth_specific_details_table, title=f"[bold magenta]Authentication Details ({auth_type})[/bold magenta]", border_style="magenta", expand=False)
                        )
                else:
                    auth_renderable_content.append(
                        Panel(
                            Text.from_markup("[yellow]Specified Auth ID not found in global authentications.[/yellow]"),
                            title=f"[bold magenta]Authentication Details ({auth_type})[/bold magenta]",
                            border_style="yellow",
                            expand=False,
                        )
                    )
            else:
                endpoint_details_table.add_row("Default Auth ID", "[dim]Not set[/dim]")

            current_endpoint_content = [endpoint_details_table]
            if auth_renderable_content:
                current_endpoint_content.extend(auth_renderable_content)

            endpoint_renderables.append(Panel(Group(*current_endpoint_content), title=f"[bold cyan]Endpoint: [white]{name}[/white][/bold cyan]", expand=False, border_style="blue"))
    else:
        endpoint_renderables.append(Panel("[dim]No endpoints configured.[/dim]", title="[bold steel_blue]Endpoint Configuration[/bold steel_blue]", border_style="blue"))

    if endpoint_renderables:
        if not all_endpoints:
            output_elements.extend(endpoint_renderables)
        elif len(endpoint_renderables) > 1:
            output_elements.append(Panel(Group(*endpoint_renderables), title="[bold steel_blue]Endpoint Configuration[/bold steel_blue]", border_style="blue"))
        else:
            output_elements.extend(endpoint_renderables)

    return Group(*output_elements)
