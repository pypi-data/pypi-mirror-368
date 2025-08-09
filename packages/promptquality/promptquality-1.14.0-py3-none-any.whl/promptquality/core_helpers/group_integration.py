from pydantic import UUID4

from galileo_core.helpers.group_integration import (
    delete_group_integration_collaborator as core_delete_group_integration_collaborator,
)
from galileo_core.helpers.group_integration import (
    list_group_integration_collaborators as core_list_group_integration_collaborators,
)
from galileo_core.helpers.group_integration import share_integration_with_group as core_share_integration_with_group
from galileo_core.helpers.group_integration import (
    update_group_integration_collaborator as core_update_group_integration_collaborator,
)
from galileo_core.schemas.core.collaboration_role import CollaboratorRole
from galileo_core.schemas.core.integration.group_integration import GroupIntegrationCollaboratorResponse
from promptquality.types.config import PromptQualityConfig


def share_integration_with_group(integration_id: UUID4, group_id: UUID4) -> GroupIntegrationCollaboratorResponse:
    """
    Share an integration with a group.

    Args:
        integration_id (UUID4): The ID of the integration.
        group_id (UUID4): The ID of the group.

    Returns:
        GroupIntegrationCollaboratorResponse: The response from the API.
    """
    config = PromptQualityConfig.get()
    return core_share_integration_with_group(integration_id=integration_id, group_id=group_id, config=config)


def list_group_integration_collaborators(integration_id: UUID4) -> list[GroupIntegrationCollaboratorResponse]:
    config = PromptQualityConfig.get()
    return core_list_group_integration_collaborators(integration_id=integration_id, config=config)


def update_group_integration_collaborator(
    integration_id: UUID4, group_id: UUID4, role: CollaboratorRole = CollaboratorRole.viewer
) -> GroupIntegrationCollaboratorResponse:
    config = PromptQualityConfig.get()
    return core_update_group_integration_collaborator(
        integration_id=integration_id, group_id=group_id, role=role, config=config
    )


def delete_group_integration_collaborator(integration_id: UUID4, group_id: UUID4) -> None:
    config = PromptQualityConfig.get()
    return core_delete_group_integration_collaborator(integration_id=integration_id, group_id=group_id, config=config)
