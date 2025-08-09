from pydantic import UUID4

from galileo_core.helpers.user_integration import (
    delete_user_integration_collaborator as core_delete_user_integration_collaborator,
)
from galileo_core.helpers.user_integration import (
    list_user_integration_collaborators as core_list_user_integration_collaborators,
)
from galileo_core.helpers.user_integration import share_integration_with_user as core_share_integration_with_user
from galileo_core.helpers.user_integration import (
    update_user_integration_collaborator as core_update_user_integration_collaborator,
)
from galileo_core.schemas.core.collaboration_role import CollaboratorRole
from galileo_core.schemas.core.integration.user_integration import UserIntegrationCollaboratorResponse
from promptquality.types.config import PromptQualityConfig


def share_integration_with_user(integration_id: UUID4, user_id: UUID4) -> UserIntegrationCollaboratorResponse:
    config = PromptQualityConfig.get()
    return core_share_integration_with_user(integration_id=integration_id, user_id=user_id, config=config)


def list_user_integration_collaborators(integration_id: UUID4) -> list[UserIntegrationCollaboratorResponse]:
    config = PromptQualityConfig.get()
    return core_list_user_integration_collaborators(integration_id=integration_id, config=config)


def update_user_integration_collaborator(
    integration_id: UUID4, user_id: UUID4, role: CollaboratorRole = CollaboratorRole.viewer
) -> UserIntegrationCollaboratorResponse:
    config = PromptQualityConfig.get()
    return core_update_user_integration_collaborator(
        integration_id=integration_id, user_id=user_id, role=role, config=config
    )


def delete_user_integration_collaborator(integration_id: UUID4, user_id: UUID4) -> None:
    config = PromptQualityConfig.get()
    return core_delete_user_integration_collaborator(integration_id=integration_id, user_id=user_id, config=config)
