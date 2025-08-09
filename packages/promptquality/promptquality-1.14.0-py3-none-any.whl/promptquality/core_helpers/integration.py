from json import dumps
from typing import Optional, Union

from galileo_core.helpers.integration import (
    create_or_update_anthropic_integration as core_create_or_update_anthropic_integration,
)
from galileo_core.helpers.integration import (
    create_or_update_azure_integration as core_create_or_update_azure_integration,
)
from galileo_core.helpers.integration import create_or_update_integration as core_create_or_update_integration
from galileo_core.helpers.integration import (
    create_or_update_mistral_integration as core_create_or_update_mistral_integration,
)
from galileo_core.helpers.integration import (
    create_or_update_openai_integration as core_create_or_update_openai_integration,
)
from galileo_core.helpers.integration import (
    create_or_update_vertex_ai_integration as core_create_or_update_vertex_ai_integration,
)
from galileo_core.helpers.integration import list_integrations as core_list_integrations
from galileo_core.schemas.core.integration.anthropic_auth_type import AnthropicAuthenticationType
from galileo_core.schemas.core.integration.azure import DEFAULT_AZURE_API_VERSION, AzureModelDeployment
from galileo_core.schemas.core.integration.azure_auth_type import AzureAuthenticationType
from galileo_core.schemas.core.integration.base import IntegrationResponse
from promptquality.types.config import PromptQualityConfig


def list_integrations() -> list[IntegrationResponse]:
    """
    Returns all integrations that the user has access to.

    Returns
    -------
    List[IntegrationResponse]
        A list of integrations.
    """
    config = PromptQualityConfig.get()
    return core_list_integrations(config=config)


def create_or_update_integration(name: str, data: dict) -> IntegrationResponse:
    """
    Create or update an integration.

    Parameters
    ----------
    name : str
        A name of the new integration.

    data: dict
        All additional data for the new integration.

    Returns
    -------
    IntegrationResponse
        Response object for the created or updated integration.
    """
    config = PromptQualityConfig.get()
    return core_create_or_update_integration(name=name, data=data, config=config)


def create_or_update_openai_integration(api_key: str, organization_id: Optional[str] = None) -> IntegrationResponse:
    """
    Create or update an OpenAI integration.

    Parameters
    ----------
    api_key : str
        OpenAI API key.
    organization_id : Optional[str], optional
        OpenAI organization ID, by default None.
    Returns
    -------
    IntegrationResponse
        Response object for the created or updated integration.
    """
    config = PromptQualityConfig.get()
    return core_create_or_update_openai_integration(api_key, organization_id=organization_id, config=config)


def create_or_update_azure_integration(
    api_key: Union[str, dict[str, str]],
    endpoint: str,
    proxy: bool = False,
    authentication_type: AzureAuthenticationType = AzureAuthenticationType.api_key,
    authentication_scope: Optional[str] = None,
    headers: Optional[dict[str, str]] = None,
    api_version: str = DEFAULT_AZURE_API_VERSION,
    azure_deployment: Optional[str] = None,
    available_deployments: Optional[list[AzureModelDeployment]] = None,
    oauth2_token_url: Optional[str] = None,
    custom_header_mapping: Optional[dict[str, str]] = None,
) -> IntegrationResponse:
    """
    Create or update an Azure integration.

    Parameters
    ----------
    api_key : Union[str, dict[str, str]]
        Azure authentication key. This can be one of:
        1. Your Azure API key. If you provide this, the authentication type should be
        `AzureAuthenticationType.api_key`.
        2. A dictionary containing the Azure Entra credentials with ID and secret. If
        you use this, `AZURE_CLIENT_ID`,
        `AZURE_CLIENT_SECRET` and `AZURE_TENANT_ID` are expected to be included and the authentication type should be `AzureAuthenticationType.client_secret`.
        3. A dictionary containing the Azure Entra credentials with username and password. If
        you use this, `AZURE_CLIENT_ID`, `AZURE_USERNAME` and `AZURE_PASSWORD` are expected to be included and the authentication type should be `AzureAuthenticationType.username_password`.
        4. A dictionary containing the custom OAuth2 credentials. If you use this, `client_id`, `client_secret` are expected to be included.
    endpoint : str
        The Azure OpenAI endpoint.
    proxy : bool, optional
        Whether to use a proxy when making requests, by default False.
    authentication_type : AzureAuthenticationType, optional
        Type of authentication to use.
    authentication_scope : Optional[str], optional
        Scope for authentication, if applicable.
    headers : Optional[dict[str, str]], optional
        Additional headers to include in requests.
    api_version : str, optional
        Azure API version to use, by default DEFAULT_AZURE_API_VERSION.
    azure_deployment : Optional[str], optional
        The default deployment name to use.
    available_deployments : Optional[List[AzureModelDeployment]], optional
        Predefined deployments to avoid querying Azure for them.
    oauth2_token_url : Optional[str], optional
        OAuth2 token URL for custom OAuth2 authentication, if using `AzureAuthenticationType.custom_oauth2`.
    custom_header_mapping : Optional[Dict[str, str]], optional
        Custom header mapping for the integration, by default None.

    Returns
    -------
    IntegrationResponse
        Response object for the created or updated integration.
    """
    config = PromptQualityConfig.get()
    return core_create_or_update_azure_integration(
        dumps(api_key) if isinstance(api_key, dict) else api_key,
        endpoint=endpoint,
        proxy=proxy,
        authentication_type=authentication_type,
        authentication_scope=authentication_scope,
        headers=headers,
        api_version=api_version,
        azure_deployment=azure_deployment,
        available_deployments=available_deployments,
        oauth2_token_url=oauth2_token_url,
        custom_header_mapping=custom_header_mapping,
        config=config,
    )


def create_or_update_vertex_ai_integration(token: str) -> IntegrationResponse:
    """
    Create or update a Vertex AI integration.

    Parameters
    ----------
    token : str
        Vertex AI token.
    Returns
    -------
    IntegrationResponse
        Response object for the created or updated integration.
    """
    config = PromptQualityConfig.get()
    return core_create_or_update_vertex_ai_integration(token, config=config)


def create_or_update_anthropic_integration(
    api_key: Union[str, dict[str, str]],
    authentication_type: AnthropicAuthenticationType = AnthropicAuthenticationType.api_key,
    endpoint: Optional[str] = None,
    authentication_scope: Optional[str] = None,
    oauth2_token_url: Optional[str] = None,
    custom_header_mapping: Optional[dict[str, str]] = None,
) -> IntegrationResponse:
    """
    Create or update an Anthropic integration.

    Parameters
    ----------
    token : Union[str, dict[str, str]]
        Anthropic authentication key. This can be one of:
        1. Your Anthropic API key as a string.
        2. A dictionary containing the custom OAuth2 credentials. If you use this, `client_id`, `client_secret` are expected to be included.
    authentication_type : AnthropicAuthenticationType
        Type of authentication to use. This should be `AnthropicAuthenticationType.api_key` for API key authentication or `AnthropicAuthenticationType.custom_oauth2` for custom OAuth2 authentication.
    endpoint : Optional[str], optional
        Custom base URL for the Anthropic API.
    authentication_scope : Optional[str], optional
        Scope for authentication, if using `AnthropicAuthenticationType.custom_oauth2`.
    oauth2_token_url : Optional[str], optional
        OAuth2 token URL for custom OAuth2 authentication, if using `AnthropicAuthenticationType.custom_oauth2`.
    custom_header_mapping : Optional[Dict[str, str]], optional
        Custom header mapping for the integration, by default None.
    Returns
    -------
    IntegrationResponse
        Response object for the created or updated integration.
    """
    config = PromptQualityConfig.get()
    return core_create_or_update_anthropic_integration(
        dumps(api_key) if isinstance(api_key, dict) else api_key,
        authentication_type=authentication_type,
        endpoint=endpoint,
        authentication_scope=authentication_scope,
        oauth2_token_url=oauth2_token_url,
        custom_header_mapping=custom_header_mapping,
        config=config,
    )


def create_or_update_mistral_integration(api_key: str) -> IntegrationResponse:
    """
    Create or update a Mistral integration.

    Parameters
    ----------
    token : str
        Mistral token.
    Returns
    -------
    IntegrationResponse
        Response object for the created or updated integration.
    """
    config = PromptQualityConfig.get()
    return core_create_or_update_mistral_integration(api_key, config=config)
