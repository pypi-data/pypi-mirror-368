from pydantic import UUID4

from galileo_core.helpers.group_project import share_project_with_group as core_share_project_with_group
from galileo_core.schemas.core.collaboration_role import CollaboratorRole
from galileo_core.schemas.core.group_project import GroupProjectCollaboratorResponse
from promptquality.types.config import PromptQualityConfig


def share_project_with_group(
    project_id: UUID4, group_id: UUID4, role: CollaboratorRole = CollaboratorRole.viewer
) -> GroupProjectCollaboratorResponse:
    config = PromptQualityConfig.get()
    return core_share_project_with_group(project_id=project_id, group_id=group_id, role=role, config=config)
