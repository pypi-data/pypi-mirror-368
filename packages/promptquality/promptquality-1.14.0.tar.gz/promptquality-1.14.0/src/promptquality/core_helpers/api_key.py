from datetime import datetime
from typing import Optional

from pydantic import UUID4

from galileo_core.helpers.api_key import create_api_key as core_create_api_key
from galileo_core.helpers.api_key import delete_api_key as core_delete_api_key
from galileo_core.helpers.api_key import list_api_keys as core_list_api_keys
from galileo_core.schemas.core.api_key import ApiKeyResponse, CreateApiKeyResponse
from galileo_core.schemas.core.collaboration_role import CollaboratorRole
from promptquality.types.config import PromptQualityConfig


def create_api_key(
    description: str,
    expires_at: Optional[datetime] = None,
    project_id: Optional[UUID4] = None,
    project_role: Optional[CollaboratorRole] = None,
) -> CreateApiKeyResponse:
    config = PromptQualityConfig.get()
    return core_create_api_key(
        description=description, expires_at=expires_at, project_id=project_id, project_role=project_role, config=config
    )


def list_api_keys() -> list[ApiKeyResponse]:
    config = PromptQualityConfig.get()
    return core_list_api_keys(config=config)


def delete_api_key(api_key_id: UUID4) -> None:
    config = PromptQualityConfig.get()
    return core_delete_api_key(api_key_id=api_key_id, config=config)
