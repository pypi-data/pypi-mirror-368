import html
import logging
from typing import Callable, Dict

from kognitos.bdk.runtime.client.value import (BooleanValue, ConceptualValue,
                                               DatetimeValue, DateValue,
                                               DictionaryValue, File,
                                               FileValue, ListValue, NullValue,
                                               NumberValue, OpaqueValue,
                                               RemoteFile, RemoteTable,
                                               SensitiveValue, TableValue,
                                               TextValue, TimeValue, Value)

logger = logging.getLogger(__name__)

VALUE_FORMATTERS: Dict[str, Callable[..., str]] = {}


def register_value_formatter(value_type_name: str) -> Callable[[Callable[..., str]], Callable[..., str]]:
    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        VALUE_FORMATTERS[value_type_name] = func
        return func

    return decorator


@register_value_formatter(NumberValue.__name__)
@register_value_formatter(TextValue.__name__)
def _format_simple_value(value: Value) -> str:
    return str(value)


@register_value_formatter(NullValue.__name__)
def _format_null_value(_value: NullValue) -> str:  # type: ignore [reportArgumentType]
    return "null"


@register_value_formatter(ConceptualValue.__name__)  # type: ignore
def _format_conceptual_value(value: "ConceptualValue", format_noun_phrase_func: Callable[["ConceptualValue"], str]) -> str:
    return format_noun_phrase_func(value)


@register_value_formatter(RemoteFile.__name__)
def _format_remote_file_value(value: RemoteFile) -> str:
    return value.url


@register_value_formatter(File.__name__)
@register_value_formatter(FileValue.__name__)
def _format_file_content_value(value: Value) -> str:
    if hasattr(value, "content"):
        return str(value.content)  # pyright: ignore [reportOptionalMemberAccess]
    return str(value)


@register_value_formatter(DictionaryValue.__name__)
def _format_dictionary_value(value: DictionaryValue) -> str:
    return value.human_readable()


@register_value_formatter(ListValue.__name__)
@register_value_formatter(list.__name__)
def _format_list_value(value: "ListValue", format_value_func: Callable[["Value"], str]) -> str:
    return ", ".join(format_value_func(v) for v in value)


@register_value_formatter(BooleanValue.__name__)
def _format_boolean_value(value: BooleanValue) -> str:
    return "true" if value else "false"


@register_value_formatter(OpaqueValue.__name__)
def _format_opaque_value(value: OpaqueValue) -> str:
    return value.human_readable()


@register_value_formatter(DatetimeValue.__name__)
@register_value_formatter(DateValue.__name__)
@register_value_formatter(TimeValue.__name__)
def _format_datetime_iso_value(value: Value) -> str:
    return value.isoformat()  # pyright: ignore [reportOptionalMemberAccess]


@register_value_formatter(RemoteTable.__name__)
def _format_remote_table_value(value: RemoteTable) -> str:
    return value.url


@register_value_formatter(TableValue.__name__)
def _format_table_value(_value: TableValue) -> str:
    return _value.human_readable()


@register_value_formatter(SensitiveValue.__name__)
def _format_sensitive_value(_value: SensitiveValue) -> str:
    return "*****"


def format_value(value: "Value", format_noun_phrase_func: Callable[["ConceptualValue"], str], main_format_value_func: Callable[["Value"], str]) -> str:
    formatter = VALUE_FORMATTERS.get(type(value).__name__)
    if not formatter and isinstance(value, list):
        formatter = VALUE_FORMATTERS.get(list.__name__)

    if formatter:
        if isinstance(value, ConceptualValue):
            return formatter(value, format_noun_phrase_func=format_noun_phrase_func)
        if isinstance(value, (ListValue, list)):
            return formatter(value, format_value_func=main_format_value_func)
        return formatter(value)

    logger.warning("Unhandled value type: %s, type: %s. No specific formatter registered.", str(value), type(value).__name__)
    return html.escape(str(value))
