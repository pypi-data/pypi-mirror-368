import functools
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

import boto3
import typer
from rich.console import Console, RenderableType
from rich.pretty import pprint

from kognitos.bdk.cli.core import DefaultBDKClient
from kognitos.bdk.cli.core.client import BDKClient
from kognitos.bdk.cli.ui.common import (bdkctl_choose, build_simple_message,
                                        get_from_context_or_prompt)
from kognitos.bdk.runtime.client.concept_type import (ConceptOptionalType,
                                                      ConceptScalarType,
                                                      ConceptType,
                                                      ConceptUnionType)
from kognitos.bdk.runtime.client.offload import AWSOffload

console = Console()


def create_s3_access_policy(bucket_name: str, folder_path: str):
    """
    Creates a policy allowing access to the specified S3 folder.

    Args:
        bucket_name (str): The name of the S3 bucket.
        folder_path (str): The folder or object path within the S3 bucket.

    Returns:
        str: A JSON-formatted policy document.
    """
    policy = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": ["s3:PutObject"], "Resource": f"arn:aws:s3:::{bucket_name}/{folder_path}/*"}]}
    return json.dumps(policy, indent=4)


def get_offloading_credentials(role_arn: str, bucket_name: str, folder_name: str, duration: int = 900):
    sts_client = boto3.client("sts")
    policy = create_s3_access_policy(bucket_name, folder_name)
    assumed_role = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="bdk-runtime-client-cli", Policy=policy, DurationSeconds=duration)
    credentials = assumed_role["Credentials"]
    return AWSOffload(
        access_key=credentials.get("AccessKeyId"),
        secret_key=credentials.get("SecretAccessKey"),
        session_token=credentials.get("SessionToken"),
        region=sts_client.meta.region_name,
        bucket=bucket_name,
        folder_name=folder_name,
    )


def _is_file_type(ct: ConceptType):
    flattened_types = get_flattened_included_types_list(ct)
    return any(map(lambda x: isinstance(x, ConceptScalarType) and x.name == "CONCEPT_SCALAR_TYPE_FILE", flattened_types))


def get_flattened_included_types_list(super_type: ConceptType) -> List[ConceptType]:
    """Returns a flattened list of all the unique possible types accepted by a super type."""

    def _get_sub_types_recursive(super_type_: ConceptType) -> List[ConceptType]:
        if isinstance(super_type_, ConceptOptionalType):
            return _get_sub_types_recursive(super_type_.inner)
        if isinstance(super_type_, ConceptUnionType):
            return [individual_type for inner in super_type_.inners for individual_type in _get_sub_types_recursive(inner)]
        return [super_type_]

    sub_types = []
    for sub_type in _get_sub_types_recursive(super_type):
        if sub_type not in sub_types:
            sub_types.append(sub_type)
    return sub_types


def _format_book_choice_for_prompt(b: Any) -> str:
    """Helper function to format book choice for UI prompts."""
    return f"{b.name} - {b.version}"


def _resolve_book(client: BDKClient, app_vars: Dict, book_name: Optional[str], book_version: Optional[str]):
    name_to_use = get_from_context_or_prompt("book_name", book_name, context=app_vars, prompt_user=False)
    version_to_use = get_from_context_or_prompt("book_version", book_version, context=app_vars, prompt_user=False)

    if name_to_use and version_to_use:
        book = client.retrieve_book(name=name_to_use, version=version_to_use)
        if not book:
            console.print(f"[red bold]Error:[/red bold] Book with name '[b]{name_to_use}[/b]' and version '[b]{version_to_use}[/b]' not found.")
            raise typer.Exit(code=1)
    else:
        all_books = client.retrieve_books()
        if not all_books:
            console.print("[yellow]No books found.[/yellow]")
            raise typer.Exit(code=1)
        book = bdkctl_choose("Choose a book", all_books, _format_book_choice_for_prompt)
        if not book:
            console.print("[yellow]No book selected.[/yellow]")
            raise typer.Exit(code=1)
    return book


def get_client_with_endpoint_or_state_client(default_client: BDKClient, book: Any) -> BDKClient:
    if book and book.endpoint:
        return DefaultBDKClient.build(book.endpoint)
    return default_client


def handle_output(fn: Callable[..., Tuple[Any, RenderableType]]):
    logger = logging.getLogger("bdkctl")

    @functools.wraps(fn)
    def wrapper(ctx: typer.Context, *args, **kwargs):
        try:
            raw_output, renderable_output = fn(ctx, *args, **kwargs)
            if ctx.obj.display_raw:
                pprint(raw_output, expand_all=True)
            else:
                if isinstance(renderable_output, list):
                    for ro_item in renderable_output:
                        console.print(ro_item)
                elif renderable_output is not None:
                    console.print(renderable_output)
        except Exception as e:  # pylint: disable=broad-exception-caught
            error_message = f"{e.__class__.__name__}: {str(e)}"
            logger.error("Error in command '%s': %s", fn.__name__, str(e), exc_info=True)
            if ctx.obj.display_raw:
                error_data = {
                    "error": True,
                    "command": fn.__name__,
                    "type": e.__class__.__name__,
                    "message": str(e),
                }
                pprint(error_data, expand_all=True)
            else:
                error_panel = build_simple_message(error_message, success=False)
                console.print(error_panel)
            if not isinstance(e, typer.Exit):
                raise typer.Exit(code=1)

    return wrapper
