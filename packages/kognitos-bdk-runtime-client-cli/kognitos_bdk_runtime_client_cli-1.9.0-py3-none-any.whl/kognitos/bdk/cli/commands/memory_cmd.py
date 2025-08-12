from typing import Annotated

import typer
from rich.console import Console

from kognitos.bdk.cli.core.memory_storage import MemoryStorageBase

console = Console()

memory_app = typer.Typer(
    name="memory",
    help="Manage the persistent memory store for procedure inputs/outputs.",
    no_args_is_help=True,
    add_help_option=False,
)


@memory_app.command("show", help="Displays all key-value pairs currently in the memory store.")
def memory_show(ctx: typer.Context):
    storage: MemoryStorageBase = ctx.obj.memory_storage
    store_items = storage.get_all_items()
    if not store_items:
        console.print("[yellow]Memory store is empty.[/yellow]")
        return

    console.print("[bold steel_blue]Current Memory Store Contents:[/bold steel_blue]")
    for key, value in store_items.items():
        value_str = str(value)
        if len(value_str) > 100:
            display_value = value_str[:97] + "..."
        else:
            display_value = value_str
        console.print(f"  [bold]{key}[/bold]: {display_value}")


@memory_app.command("set", help="Sets a key-value pair in the memory store. Value is stored as a string currently.")
def memory_set(ctx: typer.Context, key: str, value: str):
    storage: MemoryStorageBase = ctx.obj.memory_storage
    storage.set_item(key, value)
    console.print(f"Set memory: [bold]{key}[/bold] = '{value}'")


@memory_app.command("clean", help="Clears all key-value pairs from the memory store.")
def memory_clean(ctx: typer.Context):
    storage: MemoryStorageBase = ctx.obj.memory_storage
    storage.clear_all()
    console.print("[bold green]Memory store cleared.[/bold green]")


@memory_app.command("delete", help="Deletes a specific key-value pair from the memory store.")
def memory_delete(ctx: typer.Context, key: str):
    storage: MemoryStorageBase = ctx.obj.memory_storage
    if storage.get_item(key) is not None:
        storage.delete_item(key)
        console.print(f"Key '[bold]{key}[/bold]' deleted from memory.")
    else:
        console.print(f"[yellow]Key '[bold]{key}[/bold]' not found in memory store.[/yellow]")


@memory_app.command("get", help="Retrieves and displays the value for a specific key from the memory store.")
def memory_get(ctx: typer.Context, key: Annotated[str, typer.Argument(help="The key of the value to retrieve.")]):
    storage: MemoryStorageBase = ctx.obj.memory_storage
    value = storage.get_item(key)
    if value is not None:
        console.print(f"[bold]{key}[/bold]:")
        console.print(value)
    else:
        console.print(f"[yellow]Key '[bold]{key}[/bold]' not found in memory.[/yellow]")
