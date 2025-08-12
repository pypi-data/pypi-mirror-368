import json
import logging
from dataclasses import dataclass, field
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Annotated, Any, Dict, Optional

import typer
import yaml
from rich.console import Console

from kognitos.bdk.cli import ui
from kognitos.bdk.cli.commands.describe_authentication_cmd import \
    describe_authentication
from kognitos.bdk.cli.commands.describe_authentications_cmd import \
    describe_authentications
from kognitos.bdk.cli.commands.describe_book_cmd import describe_book
from kognitos.bdk.cli.commands.describe_books_cmd import describe_books
from kognitos.bdk.cli.commands.describe_configurations_cmd import \
    describe_configurations
from kognitos.bdk.cli.commands.describe_environment_cmd import \
    describe_environment
from kognitos.bdk.cli.commands.describe_procedure_cmd import describe_procedure
from kognitos.bdk.cli.commands.describe_procedures_cmd import \
    describe_procedures
from kognitos.bdk.cli.commands.help_cmd import custom_help
from kognitos.bdk.cli.commands.invoke_procedure_cmd import invoke_procedure
from kognitos.bdk.cli.commands.memory_cmd import memory_app
from kognitos.bdk.cli.commands.test_connection_cmd import test_connection
from kognitos.bdk.cli.config import config_loader, configs
from kognitos.bdk.cli.core import DefaultBDKClient
from kognitos.bdk.cli.core.client import BDKClient
from kognitos.bdk.cli.core.memory_storage import (JsonFileStorage,
                                                  MemoryStorageBase)

app = typer.Typer(add_help_option=False)
console = Console()


logger = logging.getLogger("bdkctl")


@dataclass
class AppState:
    client: Optional[BDKClient] = field(default=None)
    display_raw: bool = False
    vars: Dict[str, Any] = field(default_factory=dict)
    force: bool = False
    cli_column_styles: Dict[str, Any] = field(default_factory=dict)
    loaded_config: Dict[str, Any] = field(default_factory=dict)
    memory_storage: MemoryStorageBase = field(default_factory=JsonFileStorage)

    def __post_init__(self):
        effective_endpoint = self.vars.get("endpoint")

        if not effective_endpoint:
            effective_endpoint = self.loaded_config.get("endpoint")

        if not effective_endpoint:
            effective_endpoint = configs.DEFAULT_ENDPOINT

        self.client = DefaultBDKClient.build(effective_endpoint)


def version_callback(is_requested: bool):
    if is_requested:
        current_version = pkg_version("kognitos-bdk-runtime-client-cli")
        console.print(f"bdkctl version: {current_version}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    *,
    display_raw: Optional[bool] = False,
    endpoint: Annotated[
        Optional[str],
        typer.Option(
            help="The endpoint to be used. It can be either a lambda rie endpoint (e.g., lambdarie:localhost:80) or a valid lambda ARN. If not provided, a default value will be used."
        ),
    ] = None,
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, is_eager=True),  # pylint: disable=unused-argument
    force: Annotated[
        Optional[bool],
        typer.Option(help="If set to true, it won't check compatibilty of bci protocol running on the book. Use this at your own risk. The data you get back may not be correct."),
    ] = False,
    var_file: Annotated[Optional[Path], typer.Option(help="Path to a json or yaml/yml config file with variables")] = None,
    var_string: Annotated[
        Optional[str], typer.Option(help="A json string with variables. If a var_file is also provided and variables overlap. These vars take precedence")
    ] = None,
    column_styles: Annotated[Optional[str], typer.Option(help='''JSON string to define column styles. E.g., "{\"name\": \"bold red\", \"version\": \"italic blue\"}"''')] = None,
):
    """

    All options on `Commands` can be passed through Environment Variables with the form of `BDKCTL_<OPTION_NAME>`.
    You can do the same thing for any variable that is prompted with the form of `BDKCTL_<VARIABLE_NAME>`.

    For example: `BDKCTL_BOOK_NAME=openweather` will set the book name option to `openweather`.
    """
    loaded_vars = json.loads(var_string) if var_string else {}

    vars_from_file = {}
    if var_file:
        if not var_file.exists():
            console.print(f"[red bold]Error:[/red bold] Var file not found: {var_file}")
            raise typer.Exit(code=1)
        try:
            if str(var_file).endswith(".json"):
                with open(var_file, "r", encoding="utf-8") as f:
                    vars_from_file = json.load(f)
            elif str(var_file).endswith((".yaml", ".yml")):
                with open(var_file, "r", encoding="utf-8") as f:
                    vars_from_file = yaml.safe_load(f)
            else:
                console.print(f"[red bold]Error:[/red bold] Only .json, .yaml and .yml files are supported for --var-file. Got: {var_file.suffix}")
                raise typer.Exit(code=1)
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            console.print(f"[red bold]Error:[/red bold] Failed to load var file '{var_file}': {e}")
            raise typer.Exit(code=1)
        except IOError as e:
            logger.error("IOError loading var file %s: %s", var_file, e, exc_info=True)
            console.print(f"[red bold]Error:[/red bold] Could not read var file '{var_file}': {e}")
            raise typer.Exit(code=1)
        except Exception as e:
            logger.error("Unexpected error loading var file %s: %s", var_file, e, exc_info=True)
            console.print(f"[red bold]Error:[/red bold] An unexpected error occurred while loading var file '{var_file}': {e}")
            raise typer.Exit(code=1)

    all_vars = {**vars_from_file, **loaded_vars}

    parsed_cli_column_styles = {}
    if column_styles:
        try:
            parsed_cli_column_styles = json.loads(column_styles)
            if not isinstance(parsed_cli_column_styles, dict):
                raise ValueError("Column styles must be a JSON object (dictionary).")
            for k, v_style in parsed_cli_column_styles.items():
                if not isinstance(k, str) or not isinstance(v_style, str):
                    raise ValueError("Column style keys and values must be strings.")
        except json.JSONDecodeError as e:
            console.print(f"[red bold]Error:[/red bold] Invalid JSON string for --column-styles: {e}")
            raise typer.Exit(code=1)
        except ValueError as e:
            console.print(f"[red bold]Error in --column-styles:[/red bold] {e}")
            raise typer.Exit(code=1)

    file_loaded_config = config_loader.load_config()

    bdkctl_endpoint = ui.common.get_from_context_or_prompt(
        "endpoint",
        value=endpoint,
        context=all_vars,
        prompt_user=False,
    )

    if not bdkctl_endpoint:
        bdkctl_endpoint = file_loaded_config.get("endpoint")

    if not bdkctl_endpoint:
        bdkctl_endpoint = configs.DEFAULT_ENDPOINT

    if "endpoint" not in all_vars or not all_vars.get("endpoint"):
        all_vars["endpoint"] = bdkctl_endpoint

    ctx.obj = AppState(
        display_raw=display_raw or False,
        vars=all_vars,
        force=force or False,
        cli_column_styles=parsed_cli_column_styles,
        loaded_config=file_loaded_config,
    )


app.command(name="describe-books", add_help_option=False)(describe_books)
app.command(name="describe-book", add_help_option=False)(describe_book)
app.command(name="describe-configurations", add_help_option=False)(describe_configurations)
app.command(name="describe-procedures", add_help_option=False)(describe_procedures)
app.command(name="describe-procedure", add_help_option=False)(describe_procedure)
app.command(name="describe-authentications", add_help_option=False)(describe_authentications)
app.command(name="describe-authentication", add_help_option=False)(describe_authentication)
app.command(name="describe-environment", add_help_option=False)(describe_environment)
app.command(name="test-connection", add_help_option=False)(test_connection)
app.command(name="invoke-procedure", add_help_option=False)(invoke_procedure)
app.command(name="help", help="Shows help for bdkctl commands or a specific command.")(custom_help)

app.add_typer(memory_app)


if __name__ == "__main__":
    app()
