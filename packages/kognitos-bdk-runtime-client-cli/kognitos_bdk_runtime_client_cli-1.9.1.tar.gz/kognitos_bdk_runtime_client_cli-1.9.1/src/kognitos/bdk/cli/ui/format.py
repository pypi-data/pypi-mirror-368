import logging

from kognitos.bdk.runtime.client.book_authentication_descriptor import (
    BookAuthenticationDescriptor, BookCustomAuthenticationDescriptor,
    BookOAuthAuthenticationDescriptor, OauthFlow, OauthProvider)
from kognitos.bdk.runtime.client.credential_descriptor import CredentialType
from kognitos.bdk.runtime.client.noun_phrase import NounPhrase, NounPhrases

from .formatters import format_concept_type as _format_concept_type_dispatcher
from .formatters import format_value as _format_value_dispatcher

logger = logging.getLogger("kognitos.bdk.cli.ui.format")


def format_noun_phrase(np: NounPhrase) -> str:
    mods = " ".join(np.modifiers or [])
    head_str = np.head
    if isinstance(np.head, NounPhrase):
        head_str = format_noun_phrase(np.head)
    return (f"{mods} " if mods else "") + head_str


def format_noun_phrases(nps: NounPhrases) -> str:
    return "'s ".join(map(format_noun_phrase, nps.noun_phrases))


def format_concept_type(concept_type) -> str:
    return _format_concept_type_dispatcher(concept_type)


def format_value(value) -> str:
    return _format_value_dispatcher(value, format_noun_phrase_func=format_noun_phrase, main_format_value_func=format_value)


def format_credential_type(credential_type: CredentialType) -> str:
    if credential_type == CredentialType.CREDENTIAL_TYPE_TEXT:
        return "text"
    if credential_type == CredentialType.CREDENTIAL_TYPE_SENSITIVE_TEXT:
        return "sensitive text"
    logger.warning("Unknown credential type: %s", str(credential_type))
    return credential_type.name


def format_oauth_provider(provider: OauthProvider) -> str:
    if provider == OauthProvider.OAUTH_PROVIDER_GOOGLE:
        return "Google"
    if provider == OauthProvider.OAUTH_PROVIDER_MICROSOFT:
        return "Microsoft"
    if provider == OauthProvider.OAUTH_PROVIDER_GENERIC:
        return "Generic"
    logger.warning("Unknown provider: %s", str(provider))
    return provider.name


def _build_custom_authentication_title(authentication: BookCustomAuthenticationDescriptor) -> str:
    return f"""Connect using {' and '.join(c.label for c in authentication.credentials)} ({authentication.id})"""


def _build_oauth_authentication_title(authentication: BookOAuthAuthenticationDescriptor) -> str:
    return f"""Connect using OAuth with {format_oauth_provider(authentication.provider)} ({authentication.id})"""


def format_authentication_title(auth: BookAuthenticationDescriptor) -> str:
    auth_mappings = {
        BookCustomAuthenticationDescriptor: _build_custom_authentication_title,
        BookOAuthAuthenticationDescriptor: _build_oauth_authentication_title,
    }
    formatter_func = auth_mappings.get(type(auth))
    if formatter_func:
        return formatter_func(auth)
    logger.warning("Unknown authentication type: %s", type(auth).__name__)
    return f"{auth.name or 'Unknown Authentication'} ({auth.id})"


def format_oauth_flow(flow: OauthFlow) -> str:
    if flow == OauthFlow.OAUTH_FLOW_AUTHORIZATION_CODE:
        return "Authorization Code"
    if flow == OauthFlow.OAUTH_FLOW_CLIENT_CREDENTIALS:
        return "Client Credentials"

    logger.warning("Unknown flow: %s", str(flow))
    return flow.name
