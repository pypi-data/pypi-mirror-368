from typing import Optional

from pydantic import UUID4

from galileo_core.helpers.group import add_users_to_group as core_add_users_to_group
from galileo_core.helpers.group import create_group as core_create_group
from galileo_core.helpers.group import list_groups as core_list_groups
from galileo_core.schemas.core.group import AddGroupMemberResponse, CreateGroupResponse
from galileo_core.schemas.core.group_role import GroupRole
from galileo_core.schemas.core.group_visibility import GroupVisibility
from promptquality.types.config import PromptQualityConfig


def add_users_to_group(
    group_id: UUID4, user_ids: list[UUID4], role: GroupRole = GroupRole.member
) -> list[AddGroupMemberResponse]:
    config = PromptQualityConfig.get()
    return core_add_users_to_group(group_id=group_id, user_ids=user_ids, role=role, config=config)


def create_group(
    name: str, description: Optional[str] = None, visibility: GroupVisibility = GroupVisibility.public
) -> CreateGroupResponse:
    config = PromptQualityConfig.get()
    return core_create_group(name=name, description=description, visibility=visibility, config=config)


def list_groups() -> list[CreateGroupResponse]:
    config = PromptQualityConfig.get()
    return core_list_groups(config=config)
