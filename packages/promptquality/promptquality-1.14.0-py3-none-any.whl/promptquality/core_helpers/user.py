from typing import Optional

from pydantic import UUID4

from galileo_core.helpers.user import create_user as core_create_user
from galileo_core.helpers.user import get_current_user as core_get_current_user
from galileo_core.helpers.user import invite_users as core_invite_users
from galileo_core.helpers.user import list_users as core_list_users
from galileo_core.helpers.user import update_user as core_update_user
from galileo_core.schemas.core.auth_method import AuthMethod
from galileo_core.schemas.core.user import CreateUserResponse, User
from galileo_core.schemas.core.user_role import UserRole
from promptquality.types.config import PromptQualityConfig


def get_current_user() -> User:
    config = PromptQualityConfig.get()
    return core_get_current_user(config=config)


def create_user(email: str, password: str, role: UserRole = UserRole.read_only) -> CreateUserResponse:
    """
    Create user.
    Parameters
    ----------
    email: str
        The user's email address.
    password: str
        The user's password.
    role: UserRole = UserRole.read_only
        The user's assigned role.

    Returns
    -------
    CreateUserResponse
        Created user.
    """
    config = PromptQualityConfig.get()
    return core_create_user(email=email, password=password, role=role, config=config)


def invite_users(
    emails: list[str],
    role: UserRole = UserRole.user,
    group_ids: Optional[list[UUID4]] = None,
    auth_method: AuthMethod = AuthMethod.email,
) -> None:
    """
    Invite users.

    Parameters
    ----------
    emails : List[str]
        List of emails to invite.
    role : UserRole, optional
        Roles to grant invited users, by default UserRole.user
    group_ids : Optional[List[UUID4]], optional
        Group IDs to add the users to, by default None, which means they are not added to any group.
    auth_method : AuthMethod, optional
        Authentication method to use, by default AuthMethod.email
    """
    config = PromptQualityConfig.get()
    return core_invite_users(emails=emails, role=role, group_ids=group_ids, auth_method=auth_method, config=config)


def list_users() -> list[User]:
    """
    List all users.

    Returns
    -------
    List[User]
        List of all users.
    """
    config = PromptQualityConfig.get()
    return core_list_users(config=config)


def update_user(user_id: UUID4, role: UserRole = UserRole.user) -> User:
    """
    Update user.

    Parameters
    ----------
    user_id : User.id
        User ID to update.
    role : UserRole
        New role to assign to the user.

    Returns
    -------
    User
        Updated user.
    """
    config = PromptQualityConfig.get()
    return core_update_user(user_id=user_id, role=role, config=config)
