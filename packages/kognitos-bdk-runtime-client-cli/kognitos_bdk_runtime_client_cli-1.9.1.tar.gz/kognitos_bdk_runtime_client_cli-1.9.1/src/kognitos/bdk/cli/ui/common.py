"""Set of common functions to have a unified style for bdkctl"""

import os
from typing import Any, Callable, Dict, List, Optional

import questionary
from prompt_toolkit.styles import Style, merge_styles
from questionary import constants as q_constants
from rich.console import RenderableType
from rich.panel import Panel

try:
    default_questionary_style = q_constants.DEFAULT_STYLE_CLASSIC
except AttributeError:
    default_questionary_style = Style([])


custom_prompt_style = merge_styles(
    [
        Style.from_dict(
            {
                "bold": "bold",
                "dim": "#666666",
            }
        ),
        default_questionary_style,
    ]
)


def get_from_context_or_prompt(var_name: str, value: Any = None, *, context: Optional[Dict] = None, var_info: str = "", prompt_user=True, raise_on_empty=True) -> str:
    """
    Tries to get a variable value from:
    1) Value
    2) Context.
    3) If var is not present in context, we try to get it from the ENVIRONMENT.
    4) If var is not present in environment, we prompt the user for it.
    """

    def format_var_name_as_env_var():
        return var_name.upper().replace(" ", "_")

    if value:
        return value

    if context:
        value = context.get(var_name) or context.get(var_name.lower()) or context.get(var_name.upper())

    if not value:
        var_name_as_env_var = format_var_name_as_env_var()
        value = os.getenv("BDKCTL_" + var_name_as_env_var) or os.getenv("bdkctl_" + var_name_as_env_var.lower())

    if not value and prompt_user:
        value = questionary.text(f"{var_name}" + (f" ({var_info})" if var_info else ""), style=custom_prompt_style).ask()  # type: ignore[arg-type]

    if raise_on_empty and value == "":
        raise ValueError(f"Variable {var_name} is empty")

    return value


def build_bdkctl_list(str_list: Optional[List[str]], tab_size=4) -> str:
    if not str_list:
        return ""

    return "".join([f"\n{' ' * tab_size} - {s}" for s in str_list]).replace("\n", "", 1)


def build_bdkctl_panel(renderable: RenderableType, title: str) -> Panel:
    return Panel(renderable, title=title)


def bdkctl_choose(prompt: str, choices: List[Any], format_function: Optional[Callable] = None) -> Any:
    """
    Prompts the user to choose from one of `choices`.
    If there's only one choice, we "autoselect" that choice instead of asking.
    """

    def format_choices():
        return [{"name": format_function(c) if format_function else str(c), "value": i} for i, c in enumerate(choices)]

    if not choices:
        raise ValueError("Nothing to choose from")

    if len(choices) == 1:
        choice = choices[0]
    else:
        choice_index = questionary.select(prompt, choices=format_choices(), style=custom_prompt_style).ask()  # type: ignore[arg-type]
        if choice_index is None:
            return None
        choice = choices[choice_index]

    return choice


def prompt_for_value(_concept_descriptor: Any, prompt_message: RenderableType) -> Optional[str]:
    """Prompts the user for a value, handling empty input for non-required concepts."""
    response = questionary.text(str(prompt_message), style=custom_prompt_style).ask()  # type: ignore[arg-type]
    return response


def build_simple_message(message: str, *, success: bool = True) -> Panel:
    """Builds a simple panel message, green for success, red for failure."""
    style = "green" if success else "red"
    return Panel(message, style=style, title="Status", border_style=style)
