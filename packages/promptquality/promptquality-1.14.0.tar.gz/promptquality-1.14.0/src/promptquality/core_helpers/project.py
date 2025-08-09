from typing import Optional

from pydantic import UUID4

from galileo_core.helpers.project import create_project as core_create_project
from galileo_core.helpers.project import get_project as core_get_project
from galileo_core.helpers.project import get_project_from_id as core_get_project_from_id
from galileo_core.helpers.project import get_project_from_name as core_get_project_from_name
from galileo_core.helpers.project import get_projects as core_get_projects
from galileo_core.schemas.core.project import ProjectResponse, ProjectType
from promptquality.types.config import PromptQualityConfig


def get_project(project_id: Optional[UUID4] = None, project_name: Optional[str] = None) -> Optional[ProjectResponse]:
    config = PromptQualityConfig.get()
    return core_get_project(
        project_id=project_id, project_name=project_name, project_type=ProjectType.prompt_evaluation, config=config
    )


def create_project(request: ProjectResponse) -> ProjectResponse:
    config = PromptQualityConfig.get()
    return core_create_project(request=request, config=config)


def get_projects() -> list[ProjectResponse]:
    config = PromptQualityConfig.get()
    return core_get_projects(project_type=ProjectType.prompt_evaluation, config=config)


def get_project_from_id(project_id: UUID4) -> ProjectResponse:
    config = PromptQualityConfig.get()
    return core_get_project_from_id(project_id=project_id, config=config)


def get_project_from_name(project_name: str, raise_if_missing: bool = True) -> Optional[ProjectResponse]:
    config = PromptQualityConfig.get()
    return core_get_project_from_name(
        project_name=project_name,
        project_type=ProjectType.prompt_evaluation,
        raise_if_missing=raise_if_missing,
        config=config,
    )
