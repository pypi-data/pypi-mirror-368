from typing import Optional, Union
from warnings import warn

from galileo_core.schemas.core.integration.azure import DEFAULT_AZURE_API_VERSION, AzureModelDeployment
from galileo_core.schemas.core.integration.azure_auth_type import AzureAuthenticationType
from promptquality.core_helpers.integration import (
    create_or_update_azure_integration,
    create_or_update_openai_integration,
)


def add_openai_integration(api_key: str, organization_id: Optional[str] = None) -> None:
    """
    Add an OpenAI integration to your Galileo account.

    If you add an integration while one already exists, the new integration will
    overwrite the old one.

    Parameters
    ----------
    api_key : str
        Your OpenAI API key.
    organization_id : Optional[str], optional
        Organization ID, if you want to include it in OpenAI requests, by default None
    """
    warn(
        "The add_openai_integration function is deprecated and will be removed in a future version. Please use create_or_update_openai_integration instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    create_or_update_openai_integration(api_key=api_key, organization_id=organization_id)


def add_azure_integration(
    api_key: Union[str, dict[str, str]],
    endpoint: str,
    authentication_type: AzureAuthenticationType = AzureAuthenticationType.api_key,
    authentication_scope: Optional[str] = None,
    available_deployments: Optional[list[AzureModelDeployment]] = None,
    headers: Optional[dict[str, str]] = None,
    proxy: bool = False,
    api_version: str = DEFAULT_AZURE_API_VERSION,
    azure_deployment: Optional[str] = None,
) -> None:
    """
    Add an Azure integration to your Galileo account.

    If you add an integration while one already exists, the new integration will
    overwrite the old one.

    Parameters
    ----------
    api_key : str
        Azure authentication key. This can be one of:
        1. Your Azure API key. If you provide this, the authentication type should be
        `AzureAuthenticationType.api_key`.
        2. A dictionary containing the Azure Entra credentials with ID and secret. If
        you use this, `AZURE_CLIENT_ID`,
        `AZURE_CLIENT_SECRET` and `AZURE_TENANT_ID` are expected to be included and the authentication type should be `AzureAuthenticationType.client_secret`.
        3. A dictionary containing the Azure Entra credentials with username and password. If
        you use this, `AZURE_CLIENT_ID`, `AZURE_USERNAME` and `AZURE_PASSWORD` are expected to be included and the authentication type should be `AzureAuthenticationType.username_password`.
    endpoint : str
        The endpoint to use for the Azure API.
    authentication_type : AzureAuthenticationType, optional
        The type of authentication to use, by default AzureAuthenticationType.api_key.
    authentication_scope : Optional[str], optional
        The scope to use for authentication with Azure Entra, by default None, which translates to the default scope
        for Azure Cognitive Services (https://cognitiveservices.azure.com/.default).
    available_deployments : Optional[List[AzureModelDeployment]], optional
        The available deployments for the model. If provided, we won't try to get it from Azure directly. This list should contain values with keys `model` and `id` where the values match the model ID [1] and `id` matches the deployment ID, by default None.
        [1]: https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models
    headers : Optional[Dict[str, str]], optional
        Headers to use for making requests to Azure, by default None.
    proxy : bool, optional
        Whether the endpoint provided is a proxy endpoint. If your endpoint doesn't contain `azure` in the URL, it is likely a proxy, by default False.
    api_version : Optional[str], optional
        The API version to use for the Azure API, by default None, which translates to the latest stable OpenAI API version.
    azure_deployment : Optional[str], optional
        The Azure deployment name to use, by default None.
    """
    warn(
        "The add_azure_integration function is deprecated and will be removed in a future version. Please use create_or_update_azure_integration instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    create_or_update_azure_integration(
        api_key=api_key,
        endpoint=endpoint,
        authentication_type=authentication_type,
        authentication_scope=authentication_scope,
        available_deployments=available_deployments,
        headers=headers,
        proxy=proxy,
        api_version=api_version,
        azure_deployment=azure_deployment,
    )
