import logging
from typing import Annotated, Any, List, Optional, Tuple

import typer
from rich.console import Console, RenderableType

from kognitos.bdk.cli.core.client import BDKClient
from kognitos.bdk.cli.core.memory_storage import MemoryStorageBase
from kognitos.bdk.cli.ui.authentication import prompt_authentications
from kognitos.bdk.cli.ui.common import (bdkctl_choose,
                                        get_from_context_or_prompt)
from kognitos.bdk.cli.ui.procedure import (build_procedure_error,
                                           build_procedure_result,
                                           prompt_inputs,
                                           prompt_save_output_to_memory)
from kognitos.bdk.cli.utils import (_resolve_book,
                                    get_client_with_endpoint_or_state_client,
                                    get_offloading_credentials, handle_output)
from kognitos.bdk.runtime.client.exceptions import BDKRuntimeClientError
from kognitos.bdk.runtime.client.offload import AWSOffload

console = Console()
logger = logging.getLogger("bdkctl")


@handle_output
def invoke_procedure(
    ctx: typer.Context,
    *,
    book_name: Optional[str] = None,
    book_version: Optional[str] = None,
    procedure_id: Optional[str] = None,
    prompt_optional: Annotated[
        bool,
        typer.Option(help="If set to true, it'll prompt for optional inputs as well."),
    ] = False,
    aws_offload: Annotated[
        Optional[str],
        typer.Option(help="Specify the S3 bucket name and folder path for large inputs/outputs, e.g., 'my-bucket/my-folder'."),
    ] = None,
    aws_role_to_assume: Annotated[
        Optional[str],
        typer.Option(help="ARN of the IAM role to assume for S3 access. If not provided, uses default credentials."),
    ] = None,
) -> Tuple[Any, RenderableType]:
    """Invokes a procedure on a book"""
    book = _resolve_book(ctx.obj.client, ctx.obj.vars, book_name=book_name, book_version=book_version)
    client: BDKClient = get_client_with_endpoint_or_state_client(ctx.obj.client, book)
    procedure_id_to_use = get_from_context_or_prompt("procedure_id", procedure_id, context=ctx.obj.vars, prompt_user=False)
    selected_procedure = None

    if procedure_id_to_use:
        selected_procedure = client.retrieve_procedure(name=book.name, version=book.version, procedure_id=procedure_id_to_use, include_connect=True)
        if not selected_procedure:
            console.print(f"[red bold]Error:[/red bold] Procedure with ID '[b]{procedure_id_to_use}[/b]' not found in book '[b]{book.name} v{book.version}[/b]'.")
            raise typer.Exit(code=1)
    else:
        all_procedures_raw = client.retrieve_procedures(name=book.name, version=book.version, include_connect=True)
        all_procedures = [p for p in all_procedures_raw if getattr(p, "id", None) != "connect"]

        if not all_procedures:
            console.print(f"[yellow]No procedures found for book '[b]{book.name} v{book.version}[/b]'.[/yellow]")
            return None, ""
        selected_procedure = bdkctl_choose("Choose a procedure to invoke", all_procedures, lambda p: p.id)
        if not selected_procedure:
            console.print("[yellow]No procedure selected.[/yellow]")
            raise typer.Exit(code=1)

    if not hasattr(selected_procedure, "inputs"):
        selected_procedure = client.retrieve_procedure(name=book.name, version=book.version, procedure_id=selected_procedure.id, include_connect=True)
        if not selected_procedure:
            console.print(f"[red bold]Error:[/red bold] Could not retrieve full details for procedure '[b]{selected_procedure.id}[/b]'.")
            raise typer.Exit(code=1)

    auth_id_for_invocation: Optional[str] = None
    final_auth_credentials: Optional[List[Tuple[str, Any]]] = None

    connection_is_required = getattr(book, "connection_required", False)

    initial_auth_id_from_context = get_from_context_or_prompt("authentication_id", None, context=ctx.obj.vars, prompt_user=False)

    if initial_auth_id_from_context:
        auth_id_for_invocation = initial_auth_id_from_context
    elif book.authentications:
        auth_selection_details = prompt_authentications(
            authentications=book.authentications, authentication_id=None, config_vars=ctx.obj.vars, allow_skip=(not connection_is_required)
        )

        if auth_selection_details:
            auth_id_for_invocation = auth_selection_details[0]
            final_auth_credentials = auth_selection_details[1]
        elif connection_is_required:
            console.print("[red bold]Error: This book requires authentication, but none was selected.[/red bold]")
            raise typer.Exit(code=1)

    elif connection_is_required:
        console.print(
            f"[red bold]Error: Procedure '[bold]{selected_procedure.id}[/bold]' (in book '{book.name}') requires authentication, "
            "but no authentication methods are defined for the book.[/red bold]"
        )
        raise typer.Exit(code=1)

    formatted_inputs, _auth_id_returned_by_prompt_inputs, _effective_configs = prompt_inputs(
        procedure=selected_procedure,
        _book_configurations=book.configurations,
        context_vars=ctx.obj.vars,
        memory_storage=ctx.obj.memory_storage,
        prompt_optional_inputs=prompt_optional,
        force_prompt=ctx.obj.force,
        explicit_auth_id=auth_id_for_invocation,
    )

    aws_offload_object: Optional[AWSOffload] = None
    if aws_offload:
        s3_parts = aws_offload.split("/", 1)
        s3_bucket = s3_parts[0]
        s3_folder = s3_parts[1] if len(s3_parts) > 1 else ""

        if aws_role_to_assume:
            aws_offload_object = get_offloading_credentials(role_arn=aws_role_to_assume, bucket_name=s3_bucket, folder_name=s3_folder)
        else:
            logger.warning("AWS Offload path provided but no IAM role to assume. Offloading might not work as expected without credentials.")

    try:
        invocation_result = client.invoke_procedure(
            name=book.name,
            version=book.version,
            procedure_id=selected_procedure.id,
            input_concepts=formatted_inputs,
            authentication_id=auth_id_for_invocation,
            authentication_credentials=final_auth_credentials,
            offload=aws_offload_object,
        )
        outputs_to_render = invocation_result if isinstance(invocation_result, list) else getattr(invocation_result, "outputs", [])

        if outputs_to_render and isinstance(outputs_to_render, list):
            console.print("[bold steel_blue]Procedure Invocation Successful.[/bold steel_blue]")
            storage: MemoryStorageBase = ctx.obj.memory_storage
            for output_concept in outputs_to_render:
                prompt_save_output_to_memory(output_concept, storage, console)

        return invocation_result, build_procedure_result(outputs_to_render)
    except BDKRuntimeClientError as bdk_e:
        logger.error("BDK Error invoking procedure '%s' on book '%s v%s': %s", selected_procedure.id, book.name, book.version, bdk_e, exc_info=True)
        error_message = getattr(bdk_e, "message", str(bdk_e))
        console.print(build_procedure_error(message=error_message, title=f"Procedure Invocation Error: {selected_procedure.id}"))
        raise typer.Exit(1)
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Unexpected Error invoking procedure '%s' on book '%s v%s': %s", selected_procedure.id, book.name, book.version, e, exc_info=True)
        console.print(build_procedure_error(message=str(e), title=f"Unexpected Error with: {selected_procedure.id}"))
        raise typer.Exit(1)
