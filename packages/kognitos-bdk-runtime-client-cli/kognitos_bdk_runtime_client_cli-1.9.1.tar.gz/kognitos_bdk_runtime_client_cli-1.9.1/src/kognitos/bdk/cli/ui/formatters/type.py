import logging

from kognitos.bdk.runtime.client.concept_type import (ConceptAnyType,
                                                      ConceptDictionaryType,
                                                      ConceptEnumType,
                                                      ConceptListType,
                                                      ConceptOpaqueType,
                                                      ConceptOptionalType,
                                                      ConceptScalarType,
                                                      ConceptSelfType,
                                                      ConceptSensitiveType,
                                                      ConceptTableType,
                                                      ConceptType,
                                                      ConceptUnionType)

logger = logging.getLogger(__name__)


CONCEPT_TYPE_FORMATTERS = {}


def register_concept_type_formatter(concept_type_class):
    def decorator(func):
        CONCEPT_TYPE_FORMATTERS[concept_type_class] = func
        return func

    return decorator


@register_concept_type_formatter(ConceptScalarType)
def _format_concept_scalar_type(concept_type: ConceptScalarType) -> str:
    scalar_type_mapping = {
        ConceptScalarType.CONCEPT_SCALAR_TYPE_BOOLEAN: "boolean",
        ConceptScalarType.CONCEPT_SCALAR_TYPE_CONCEPTUAL: "noun",
        ConceptScalarType.CONCEPT_SCALAR_TYPE_DATE: "date",
        ConceptScalarType.CONCEPT_SCALAR_TYPE_DATETIME: "datetime",
        ConceptScalarType.CONCEPT_SCALAR_TYPE_FILE: "file",
        ConceptScalarType.CONCEPT_SCALAR_TYPE_TEXT: "text",
        ConceptScalarType.CONCEPT_SCALAR_TYPE_TIME: "time",
        ConceptScalarType.CONCEPT_SCALAR_TYPE_NUMBER: "number",
    }
    mapped_type = scalar_type_mapping.get(concept_type)
    if not mapped_type:
        logger.warning("Unknown scalar type: %s", str(concept_type))
        if hasattr(concept_type, "name"):
            return concept_type.name
        return str(concept_type)
    return mapped_type


@register_concept_type_formatter(ConceptListType)
def _format_concept_list_type(concept_type: ConceptListType) -> str:
    return f"List[{format_concept_type(concept_type.inner)}]"


@register_concept_type_formatter(ConceptDictionaryType)
def _format_concept_dictionary_type(_concept_type: ConceptDictionaryType) -> str:
    return "Dict"


@register_concept_type_formatter(ConceptOpaqueType)
def _format_concept_opaque_type(concept_type: ConceptOpaqueType) -> str:
    return f"Opaque[{','.join(str(i) for i in concept_type.is_a)}]" if concept_type.is_a else "Opaque"


@register_concept_type_formatter(ConceptOptionalType)
def _format_concept_optional_type(concept_type: ConceptOptionalType) -> str:
    return f"Optional[{format_concept_type(concept_type.inner)}]"


@register_concept_type_formatter(ConceptTableType)
def _format_concept_table_type(_concept_type: ConceptTableType) -> str:
    return "Table"


@register_concept_type_formatter(ConceptAnyType)
def _format_concept_any_type(_concept_type: ConceptAnyType) -> str:
    return "Any"


@register_concept_type_formatter(ConceptUnionType)
def _format_concept_union_type(concept_type: ConceptUnionType) -> str:
    return " or ".join(format_concept_type(inner_type) for inner_type in concept_type.inners)


@register_concept_type_formatter(ConceptSensitiveType)
def _format_concept_sensitive_type(_concept_type: ConceptSensitiveType) -> str:
    return "Sensitive"


@register_concept_type_formatter(ConceptEnumType)
def _format_concept_enum_type(_concept_type: ConceptEnumType) -> str:
    return "Enum"


@register_concept_type_formatter(ConceptSelfType)
def _format_concept_self_type(_concept_type: ConceptSelfType) -> str:
    return "Self"


def format_concept_type(concept_type: ConceptType) -> str:
    formatter = CONCEPT_TYPE_FORMATTERS.get(type(concept_type))
    if formatter:
        return formatter(concept_type)

    logger.warning("Unknown concept type instance: %s, type: %s. No specific formatter registered.", str(concept_type), type(concept_type).__name__)

    if hasattr(concept_type, "name"):
        return concept_type.name
    return str(concept_type)
