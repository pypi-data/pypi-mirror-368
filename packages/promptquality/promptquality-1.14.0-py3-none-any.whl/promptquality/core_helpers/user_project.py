from pydantic import UUID4

from galileo_core.helpers.user_project import share_project_with_user as core_share_project_with_user
from galileo_core.schemas.core.collaboration_role import CollaboratorRole
from galileo_core.schemas.core.user_project import UserProjectCollaboratorResponse
from promptquality.types.config import PromptQualityConfig


def share_project_with_user(
    project_id: UUID4, user_id: UUID4, role: CollaboratorRole = CollaboratorRole.viewer
) -> UserProjectCollaboratorResponse:
    config = PromptQualityConfig.get()
    return core_share_project_with_user(project_id=project_id, user_id=user_id, role=role, config=config)
