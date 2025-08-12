import json
from typing import Any, Callable, Dict, List, Optional, Tuple

import typer
from rich import box
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from kognitos.bdk.cli.core.memory_storage import MemoryStorageBase
from kognitos.bdk.cli.ui import common
from kognitos.bdk.cli.ui import format as fmt
from kognitos.bdk.runtime.client.book_procedure_descriptor import \
    BookProcedureDescriptor
from kognitos.bdk.runtime.client.concept_descriptor import ConceptDescriptor
from kognitos.bdk.runtime.client.concept_type import (ConceptDictionaryType,
                                                      ConceptOpaqueType,
                                                      ConceptOptionalType,
                                                      ConceptScalarType,
                                                      ConceptType,
                                                      ConceptUnionType)
from kognitos.bdk.runtime.client.concept_value import ConceptValue
from kognitos.bdk.runtime.client.input_concept import InputConcept
from kognitos.bdk.runtime.client.value import (ConceptualValue,
                                               DictionaryValue, NumberValue,
                                               OpaqueValue, TextValue, Value)

from .rich_table_utils import build_dynamic_table

console = Console()

PROCEDURE_FIELD_ACCESSORS: Dict[str, Callable[[Any], str]] = {
    "signature": lambda proc: str(getattr(getattr(proc, "signature", None), "english", "N/A")),
    "description": lambda proc: (getattr(proc, "short_description", None) or getattr(proc, "long_description", None) or getattr(proc, "description", None) or "N/A"),
    "connection_required": lambda proc: str(bool(getattr(proc, "connection_required", False))),
}

INPUT_VALUE_CONVERTERS: Dict[Any, Callable[[Any, ConceptType], Value]] = {}

DEFAULT_PROCEDURE_COLUMNS = ["id", "description", "signature", "connection_required"]

DEFAULT_OUTPUT_CONCEPT_COLUMNS = ["concept", "value", "type"]

DEFAULT_INPUT_CONCEPT_COLUMNS = ["concept", "type", "optional", "default_value", "description"]

CONCEPT_FIELD_ACCESSORS: Dict[str, Callable[[Any], str]] = {
    "concept": lambda cd: fmt.format_noun_phrases(nps) if (nps := getattr(cd, "noun_phrases", None)) else str(getattr(cd, "name", "N/A")),
    "type": lambda concept_item: (
        type(getattr(concept_item, "value", None)).__name__.replace("Value", "").lower()
        if hasattr(concept_item, "value") and getattr(concept_item, "value") is not None
        else fmt.format_concept_type(getattr(getattr(concept_item, "concept", concept_item), "type", "N/A"))
    ),
    "optional": lambda cd: str(bool(getattr(cd, "optional", False))),
    "default_value": lambda cd: str(fmt.format_value(val) if (val := getattr(cd, "default_value", None)) is not None else "N/A"),
    "description": lambda cd: str(getattr(getattr(cd, "concept", cd), "description", "N/A")),
    "is_secret": lambda cd: str(getattr(cd, "is_secret", "N/A")),
    "value": lambda cv: (
        str(getattr(cv.value, "text", cv.value.value_instance))
        if hasattr(cv, "value") and cv.value is not None and hasattr(cv.value, "value_instance") and not isinstance(cv.value.value_instance, list)
        else (
            (
                f"[{len(cv.value.value_instance)} {cv.value.value_instance[0].__class__.__name__.replace('Value', '')}s] (e.g., {fmt.format_value(cv.value.value_instance[0])})"
                if len(cv.value.value_instance) > 3
                else ", ".join([fmt.format_value(item) for item in cv.value.value_instance])
            )
            if hasattr(cv, "value") and cv.value is not None and isinstance(getattr(cv.value, "value_instance", None), list) and cv.value.value_instance
            else (
                ("[] (empty list)")
                if hasattr(cv, "value") and cv.value is not None and isinstance(getattr(cv.value, "value_instance", None), list)
                else fmt.format_value(getattr(cv, "value", None))
            )
        )
    ),
}


def register_input_value_converter(concept_type_key: Any):
    """Registers a converter function for a given concept type key."""

    def decorator(func: Callable[[Any, ConceptType], Value]):
        INPUT_VALUE_CONVERTERS[concept_type_key] = func
        return func

    return decorator


@register_input_value_converter(ConceptScalarType.CONCEPT_SCALAR_TYPE_TEXT)
def _convert_to_text_value(value: Any, _input_type: ConceptType) -> TextValue:
    return TextValue(str(value))


@register_input_value_converter(ConceptScalarType.CONCEPT_SCALAR_TYPE_NUMBER)
def _convert_to_number_value(value: Any, _input_type: ConceptType) -> NumberValue:
    """Converts a string or number to a NumberValue."""
    if isinstance(value, (int, float)):
        return NumberValue(float(value))
    if isinstance(value, str):
        try:
            return NumberValue(float(value))
        except ValueError as e:
            raise ValueError(f"Could not convert string '{value}' to a number.") from e
    raise ValueError(f"Cannot convert value '{value}' of type {type(value).__name__} to NumberValue for number input type.")


@register_input_value_converter(ConceptScalarType.CONCEPT_SCALAR_TYPE_CONCEPTUAL)
def _convert_to_conceptual_value(value: Any, _input_type: ConceptType) -> ConceptualValue:
    if isinstance(value, ConceptualValue):
        return value
    return ConceptualValue(head=str(value))


@register_input_value_converter(ConceptOpaqueType)
def _convert_to_opaque_value(value: Any, input_type: ConceptType) -> OpaqueValue:
    if isinstance(value, str):
        return OpaqueValue(value.encode())
    if isinstance(value, bytes):
        return OpaqueValue(value)
    raise ValueError(f"Cannot convert value '{value}' of type {type(value).__name__} to OpaqueValue for {input_type}")


@register_input_value_converter(ConceptOptionalType)
def _convert_optional_value(value: Any, input_type: ConceptType) -> Value:
    if not isinstance(input_type, ConceptOptionalType):
        raise TypeError("Input type for _convert_optional_value must be ConceptOptionalType")
    return _format_value(value, input_type.inner)


@register_input_value_converter(ConceptDictionaryType)
def _convert_to_dictionary_value(value: Any, input_type: ConceptType) -> DictionaryValue:
    if isinstance(value, dict):
        return DictionaryValue(value)
    if isinstance(value, str):
        try:
            parsed_dict = json.loads(value)
            if not isinstance(parsed_dict, dict):
                raise ValueError("Input for DictionaryType must be a JSON string representing an object.")
            return DictionaryValue(parsed_dict)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string for DictionaryType: {e}") from e
    raise ValueError(f"Cannot convert value '{value}' of type {type(value).__name__} to DictionaryValue for {input_type}")


@register_input_value_converter(ConceptUnionType)
def _convert_to_union_value(value: Any, input_type: ConceptType) -> Value:
    if not isinstance(input_type, ConceptUnionType):
        raise TypeError("Input type for _convert_to_union_value must be ConceptUnionType")

    for inner_type in input_type.inners:
        try:
            return _format_value(value, inner_type)
        except (NotImplementedError, ValueError, TypeError):
            continue
    raise ValueError(f"Value '{value}' could not be converted to any of the types in Union: {[str(it) for it in input_type.inners]}")


def _format_value(value: Any, input_type: ConceptType) -> Value:
    if isinstance(value, Value):
        if isinstance(input_type, ConceptScalarType):
            if input_type == ConceptScalarType.CONCEPT_SCALAR_TYPE_TEXT:
                if isinstance(value, TextValue):
                    return value
                if value is not None and hasattr(value, "value"):
                    primitive_content = value.value
                    if primitive_content is not None:
                        return TextValue(str(primitive_content))
                    return TextValue(str(value))
                return TextValue(str(value))

            if input_type == ConceptScalarType.CONCEPT_SCALAR_TYPE_NUMBER:
                if isinstance(value, NumberValue):
                    return value
                if isinstance(value, TextValue):
                    if value.value is None:
                        raise ValueError(f"Cannot convert None value from stored TextValue to Number for type {input_type}")
                    try:
                        return NumberValue(float(value.value))
                    except (ValueError, TypeError) as e:
                        raise ValueError(f"Cannot convert string '{value.value}' from stored TextValue to Number for type {input_type}") from e
                raise ValueError(f"Type mismatch: Stored BDK value is {type(value).__name__}, but expected Number-compatible for type {input_type}")
        return value

    converter = INPUT_VALUE_CONVERTERS.get(type(input_type))
    if not converter:
        try:
            hash(input_type)
            is_hashable = True
        except TypeError:
            is_hashable = False
        if is_hashable:
            converter = INPUT_VALUE_CONVERTERS.get(input_type)

    if converter:
        return converter(value, input_type)

    raise NotImplementedError(f"Input conversion for type '{input_type}' (class: {type(input_type).__name__}) with value '{value}' not implemented on the CLI.")


def prompt_procedures(procedures: List[BookProcedureDescriptor], procedure_id: Optional[str], config_vars: Optional[Dict], prompt: Optional[str] = None) -> BookProcedureDescriptor:
    procedure_id = common.get_from_context_or_prompt("procedure_id", procedure_id, context=config_vars, prompt_user=False)
    if procedure_id:
        procedure = next(filter(lambda p: p.id == procedure_id, procedures), None)
        if procedure:
            return procedure
    return common.bdkctl_choose(prompt or "Select a procedure", procedures, lambda p: f"{p.signature.english} ({p.id})")


def _prompt_input(concept_descriptor: ConceptDescriptor, prompt_optional=False, config_vars: Optional[Dict] = None) -> Tuple[Optional[str], Optional[str], ConceptDescriptor]:
    type_ = concept_descriptor.type
    if not prompt_optional and not _is_required_concept_type(type_):
        return None, None, concept_descriptor
    input_name = fmt.format_noun_phrases(concept_descriptor.noun_phrases)
    response = common.get_from_context_or_prompt(var_name=input_name, context=config_vars)
    return (input_name, response, concept_descriptor)


def _prompt_procedure_inputs(
    procedure: BookProcedureDescriptor, config_vars: Optional[Dict], prompt_optional: bool
) -> List[Tuple[Optional[str], Optional[str], ConceptDescriptor]]:
    return list(map(lambda i: _prompt_input(i, config_vars=config_vars, prompt_optional=prompt_optional), procedure.inputs))


def format_input(input_: Tuple[str, Any, ConceptDescriptor]) -> InputConcept:
    _, value, input_descriptor = input_
    input_type = input_descriptor.type
    formatted_value = _format_value(value, input_type)
    return InputConcept(noun_phrases=input_descriptor.noun_phrases, value=formatted_value)


def prompt_procedure_data(
    procedures: List[BookProcedureDescriptor], procedure_id: Optional[str], config_vars: Optional[Dict], prompt: Optional[str] = None, prompt_optional: bool = False
) -> Tuple[BookProcedureDescriptor, List[InputConcept]]:
    def filter_falsy_inputs(inputs: List[Tuple[Optional[str], Optional[str], ConceptDescriptor]]) -> List[Tuple[str, str, ConceptDescriptor]]:
        return list(filter(all, inputs))  # type: ignore

    selected_procedure = prompt_procedures(procedures, procedure_id, config_vars, prompt=prompt)
    inputs = _prompt_procedure_inputs(selected_procedure, config_vars, prompt_optional=prompt_optional)
    filtered_inputs = filter_falsy_inputs(inputs)
    formatted_inputs = [format_input(fi) for fi in filtered_inputs]
    return selected_procedure, formatted_inputs


def _build_result(result: ConceptValue) -> List[str]:
    res = []
    for noun_phrase in result.noun_phrases.noun_phrases:
        res += [f"{fmt.format_noun_phrase(noun_phrase)} = {fmt.format_value(result.value)}"]
    return res


def build_procedure_result(outputs: List[Any], result_columns: Optional[List[str]] = None, column_styles: Optional[Dict[str, Any]] = None) -> RenderableType:
    """Builds a Rich Renderable for procedure invocation results."""
    if not outputs:
        return Text("Procedure produced no output or output is empty.", style="yellow")
    results_table = _build_concept_table(outputs, title="Procedure Results", visible_columns=result_columns or DEFAULT_OUTPUT_CONCEPT_COLUMNS, column_styles=column_styles)

    if results_table:
        results_table.title = "Procedure Results"
        return results_table
    return Text("Failed to render procedure results.", style="red")


def _build_concept_table(concepts: List[Any], title: str, visible_columns: Optional[List[str]] = None, column_styles: Optional[Dict[str, Any]] = None) -> Optional[Table]:
    if not concepts:
        return None

    _column_styles = column_styles or {}
    is_output_like = bool(concepts and hasattr(concepts[0], "value"))
    columns_to_render = visible_columns or (DEFAULT_OUTPUT_CONCEPT_COLUMNS if is_output_like else DEFAULT_INPUT_CONCEPT_COLUMNS)

    table = Table(box=box.SIMPLE, padding=(0, 1), show_header=True)

    for col_name_raw in columns_to_render:
        attr_name = col_name_raw.lower().replace(" ", "_")
        header_display = col_name_raw.replace("_", " ").capitalize()
        style_key_prefix = title.lower()
        style_key = f"{style_key_prefix}.{attr_name}"
        style_conf = _column_styles.get(style_key, _column_styles.get(attr_name, {}))
        table.add_column(
            header_display,
            style=style_conf.get("header") if isinstance(style_conf, dict) else style_conf,
            justify=style_conf.get("justify", "left") if isinstance(style_conf, dict) else "left",
        )

    for concept_desc in concepts:
        row_data = []
        for col_name_raw in columns_to_render:
            attr_name = col_name_raw.lower().replace(" ", "_")
            value = "N/A"

            if attr_name in CONCEPT_FIELD_ACCESSORS:
                try:
                    value = CONCEPT_FIELD_ACCESSORS[attr_name](concept_desc)
                except ValueError:
                    value = "Conversion Error"
                except AttributeError:
                    value = "Attribute Error"
                except Exception as e_general:
                    print(f"Unexpected error in accessor for {attr_name} on concept: {e_general}")
                    value = "Accessor Error!"
            else:
                if hasattr(concept_desc, attr_name):
                    raw_val = getattr(concept_desc, attr_name)
                elif hasattr(concept_desc, "concept") and hasattr(getattr(concept_desc, "concept"), attr_name):
                    raw_val = getattr(getattr(concept_desc, "concept"), attr_name)
                else:
                    raw_val = "N/A"

                if hasattr(raw_val, "name"):
                    value = str(getattr(raw_val, "name"))
                elif isinstance(raw_val, bool):
                    value = str(raw_val)
                elif raw_val is None:
                    value = "N/A"
                else:
                    value = str(raw_val)

            row_data.append(str(value) if value is not None else "N/A")
        table.add_row(*row_data)
    return table


def build_procedure(
    procedure: Any,
    input_columns: Optional[List[str]] = None,
    output_columns: Optional[List[str]] = None,
    column_styles: Optional[Dict[str, Any]] = None,
) -> RenderableType:
    """Builds a Rich Renderable to display detailed information about a procedure."""
    if not procedure:
        return Text("Procedure details not available.", style="red")

    _column_styles = column_styles or {}
    elements: List[RenderableType] = []

    proc_id = getattr(procedure, "id", "N/A")
    proc_desc = getattr(procedure, "description", getattr(procedure, "short_description", "No description available."))
    proc_sig = getattr(getattr(procedure, "signature", None), "english", "N/A")

    basic_info_content = f"[bold]ID:[/bold] {proc_id}\n"
    basic_info_content += f"[bold]Description:[/bold] {proc_desc}\n"
    basic_info_content += f"[bold]Signature:[/bold] {proc_sig}\n"
    basic_info_content += f"[bold]Connection Required:[/bold] {getattr(procedure, 'connection_required', False)}\n"
    basic_info_content += f"[bold]Filter Capable:[/bold] {getattr(procedure, 'filter_capable', False)}\n"
    basic_info_content += f"[bold]Page Capable:[/bold] {getattr(procedure, 'page_capable', False)}"

    elements.append(Panel(Text.from_markup(basic_info_content), title="Procedure Details", expand=False, border_style="blue"))

    inputs = getattr(procedure, "inputs", [])
    inputs_table = _build_concept_table(inputs, "Inputs", visible_columns=input_columns, column_styles=_column_styles)
    if inputs_table:
        elements.append(Panel(inputs_table, title="Inputs", border_style="green", expand=False))
    else:
        elements.append(Panel(Text("No inputs for this procedure.", style="italic"), title="Inputs", border_style="green", expand=False))

    outputs = getattr(procedure, "outputs", [])
    outputs_table = _build_concept_table(outputs, "Outputs", visible_columns=output_columns, column_styles=_column_styles)
    if outputs_table:
        elements.append(Panel(outputs_table, title="Outputs", border_style="purple", expand=False))
    else:
        elements.append(Panel(Text("No outputs for this procedure.", style="italic"), title="Outputs", border_style="purple", expand=False))

    if not elements:
        return Text(f"No details to display for procedure ID: {proc_id}", style="yellow")

    return Group(*elements)


def build_procedures(procedures: List[Any], visible_columns: Optional[List[str]] = None, column_styles: Optional[Dict[str, Any]] = None) -> RenderableType:
    """Builds a Rich Table to display a list of procedures."""

    return build_dynamic_table(
        items=procedures,
        default_columns=DEFAULT_PROCEDURE_COLUMNS,
        field_accessors=PROCEDURE_FIELD_ACCESSORS,
        visible_columns=visible_columns,
        column_styles=column_styles,
        table_title="Available Procedures",
        no_items_message="No procedures found.",
        get_item_id_for_error=lambda proc: getattr(proc, "id", "Unknown Procedure ID"),
    )


def build_procedure_error(message: str, title: Optional[str] = "Error") -> Group:
    return Group(Rule(f"[bold red]{title}[/bold red]"), f"[red]{message}[/red]")


def _is_required_concept_type(ct: ConceptType):
    if isinstance(ct, ConceptOptionalType):
        return False
    if isinstance(ct, ConceptUnionType) and any(not _is_required_concept_type(inner) for inner in ct.inners):
        return False
    return True


def prompt_inputs(
    procedure: BookProcedureDescriptor,
    _book_configurations: List[Any],
    context_vars: Dict[str, Any],
    memory_storage: MemoryStorageBase,
    *,
    prompt_optional_inputs: bool = False,
    force_prompt: bool = False,
    explicit_auth_id: Optional[str] = None,
) -> Tuple[List[InputConcept], Optional[str], Dict[str, Any]]:
    raw_inputs = []
    _console_instance = Console()

    for concept_descriptor in procedure.inputs:
        if not prompt_optional_inputs and not _is_required_concept_type(concept_descriptor.type):
            if concept_descriptor.default_value is not None:
                pass
            else:
                continue

        input_name = fmt.format_noun_phrases(concept_descriptor.noun_phrases)
        response: Any = None
        used_from_memory = False

        if not force_prompt and memory_storage.get_all_items():
            if typer.confirm(f"Do you want to retrieve a value for input '{input_name}' from memory?", default=False):
                memory_key_to_use = typer.prompt(f"Enter the memory key for '{input_name}' (default: {input_name})", default=input_name, show_default=True)

                stored_value = memory_storage.get_item(memory_key_to_use)
                if stored_value is not None:
                    value_preview = str(stored_value)
                    if len(value_preview) > 50:
                        value_preview = value_preview[:47] + "..."
                    plain_value_preview = value_preview.replace("{", "{{").replace("}", "}}")

                    if typer.confirm(f"Found value for key '{memory_key_to_use}': '{plain_value_preview}'. Use this for '{input_name}'?", default=True):
                        response = stored_value
                        used_from_memory = True
                        _console_instance.print(f"Using value for '[bold]{input_name}[/bold]' from memory (key: '[bold]{memory_key_to_use}[/bold]').")
                    else:
                        _console_instance.print(f"Opted not to use value from memory for '{input_name}'.")
                else:
                    _console_instance.print(f"Key '[bold]{memory_key_to_use}[/bold]' not found in memory. Proceeding to manual input for '{input_name}'.")

        if not used_from_memory:
            value_from_context = context_vars.get(input_name) if not force_prompt else None

            if value_from_context is not None:
                response = value_from_context
            else:
                input_name_str = input_name
                type_str = fmt.format_concept_type(concept_descriptor.type)

                parts = [f"Enter {input_name_str} (type: {type_str}"]

                if concept_descriptor.description:
                    description_str = concept_descriptor.description
                    parts.append(f", {description_str}")

                if not _is_required_concept_type(concept_descriptor.type):
                    parts.append(", optional")

                parts.append("): ")
                prompt_message_str = "".join(parts)

                response = common.prompt_for_value(
                    concept_descriptor,
                    prompt_message=Text.from_markup(prompt_message_str),
                )

        if response is not None:
            raw_inputs.append((input_name, response, concept_descriptor))
        elif _is_required_concept_type(concept_descriptor.type) and concept_descriptor.default_value is None and not used_from_memory:
            console.print(f"[red bold]Missing required input:[/red bold] {input_name}")
            raise ValueError(f"Missing required input: {input_name}")

    formatted_inputs = [format_input(ri) for ri in raw_inputs if ri[1] is not None or (ri[2].default_value is not None and ri[1] is None)]
    auth_id_to_use = explicit_auth_id

    effective_configs = {}

    return formatted_inputs, auth_id_to_use, effective_configs


def prompt_save_output_to_memory(output_concept: Any, memory_storage: MemoryStorageBase, output_console: Console) -> None:
    """
    Prompts the user to save a procedure output to memory storage.

    Args:
        output_concept: The output concept from a procedure invocation
        memory_storage: The memory storage instance to save to
        output_console: Rich console for formatted output
    """
    concept_name_parts = getattr(output_concept, "noun_phrases", None)
    if concept_name_parts:
        concept_name = fmt.format_noun_phrases(concept_name_parts)
    else:
        concept_name = getattr(output_concept, "name", "UnknownConcept")

    concept_value = getattr(output_concept, "value", None)
    if concept_value is not None:
        plain_concept_name = concept_name
        if typer.confirm(f"Do you want to save the output for concept '{plain_concept_name}' to memory?", default=False):
            default_key = plain_concept_name
            save_key = typer.prompt(f"Enter a key to save this output (default: {default_key})", default=default_key, show_default=True)
            memory_storage.set_item(save_key, concept_value)
            output_console.print(f"Saved output for '[bold]{plain_concept_name}[/bold]' to memory with key '[bold]{save_key}[/bold]'.")
