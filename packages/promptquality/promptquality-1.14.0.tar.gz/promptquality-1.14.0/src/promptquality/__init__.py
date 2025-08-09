"""PromptQuality."""

# flake8: noqa: F401
# ruff: noqa: F401

__version__ = "1.14.0"

from galileo_core.schemas.core.auth_method import AuthMethod
from galileo_core.schemas.core.dataset import Dataset
from galileo_core.schemas.core.user import CreateUserResponse, User
from galileo_core.schemas.core.user_role import UserRole
from galileo_core.schemas.shared.customized_scorer import CustomizedScorerName
from galileo_core.schemas.shared.document import Document
from galileo_core.schemas.shared.message import Message
from galileo_core.schemas.shared.message_role import MessageRole
from galileo_core.schemas.shared.workflows.node_type import NodeType
from galileo_core.schemas.shared.workflows.step import (
    AgentStep,
    LlmStep,
    LlmStepAllowedIOType,
    RetrieverStep,
    RetrieverStepAllowedOutputType,
    StepIOType,
    StepWithChildren,
    ToolStep,
    WorkflowStep,
)
from galileo_core.schemas.shared.workflows.workflow import Workflows
from promptquality.chain_run_module import chain_run
from promptquality.constants.models import Models
from promptquality.constants.models import Models as SupportedModels
from promptquality.constants.run import TagType
from promptquality.constants.scorers import Scorers
from promptquality.core_helpers.api_key import create_api_key, delete_api_key, list_api_keys
from promptquality.core_helpers.dataset import create_dataset, get_dataset_content, list_datasets
from promptquality.core_helpers.group import add_users_to_group, create_group, list_groups
from promptquality.core_helpers.group_integration import (
    delete_group_integration_collaborator,
    list_group_integration_collaborators,
    share_integration_with_group,
    update_group_integration_collaborator,
)
from promptquality.core_helpers.group_project import share_project_with_group
from promptquality.core_helpers.integration import (
    create_or_update_anthropic_integration,
    create_or_update_azure_integration,
    create_or_update_integration,
    create_or_update_mistral_integration,
    create_or_update_openai_integration,
    create_or_update_vertex_ai_integration,
    list_integrations,
)
from promptquality.core_helpers.project import (
    create_project,
    get_project,
    get_project_from_id,
    get_project_from_name,
    get_projects,
)
from promptquality.core_helpers.user import create_user, get_current_user, invite_users, list_users, update_user
from promptquality.core_helpers.user_integration import (
    delete_user_integration_collaborator,
    list_user_integration_collaborators,
    share_integration_with_user,
    update_user_integration_collaborator,
)
from promptquality.core_helpers.user_project import share_project_with_user
from promptquality.evaluate_samples import get_evaluate_samples
from promptquality.get_metrics_module import get_metrics, get_run_metrics
from promptquality.get_rows_module import get_rows
from promptquality.get_run_scorer_jobs_module import get_run_scorer_jobs
from promptquality.get_template_module import get_template
from promptquality.helpers import get_run_from_name, get_run_settings
from promptquality.integrations import add_azure_integration, add_openai_integration
from promptquality.job_progress_module import job_progress, scorer_jobs_status
from promptquality.login_module import login
from promptquality.registered_scorers import delete_registered_scorer, list_registered_scorers, register_scorer
from promptquality.run_module import run
from promptquality.run_sweep_module import run_sweep
from promptquality.sweep_module import sweep
from promptquality.types.chains.row import NodeRow
from promptquality.types.custom_scorer import CustomScorer
from promptquality.types.customized_scorer import CustomizedChainPollScorer
from promptquality.types.evaluate_samples import EvaluateSample, EvaluateSamples
from promptquality.types.rows import PromptRow, PromptRows
from promptquality.types.run import GetJobStatusResponse, RunTag, ScorersConfiguration, TemplateVersion
from promptquality.types.settings import Settings
from promptquality.utils.dependencies import is_langchain_available
from promptquality.workflow_module import EvaluateRun

__all__ = [
    "add_azure_integration",
    "add_openai_integration",
    "add_users_to_group",
    "chain_run",
    "create_api_key",
    "create_dataset",
    "create_group",
    "create_project",
    "create_user",
    "create_or_update_azure_integration",
    "create_or_update_anthropic_integration",
    "create_or_update_integration",
    "create_or_update_openai_integration",
    "create_or_update_vertex_ai_integration",
    "create_or_update_mistral_integration",
    "delete_api_key",
    "delete_registered_scorer",
    "get_current_user",
    "get_dataset_content",
    "get_evaluate_samples",
    "get_metrics",
    "get_project_from_name",
    "get_project",
    "get_project_from_id",
    "get_projects",
    "get_rows",
    "get_run_from_name",
    "get_run_metrics",
    "get_run_settings",
    "get_run_scorer_jobs",
    "update_user",
    "get_template",
    "invite_users",
    "job_progress",
    "list_api_keys",
    "list_datasets",
    "list_groups",
    "list_registered_scorers",
    "list_integrations",
    "list_users",
    "login",
    "register_scorer",
    "run_sweep",
    "run",
    "scorer_jobs_status",
    "share_project_with_group",
    "share_project_with_user",
    "share_integration_with_user",
    "list_user_integration_collaborators",
    "update_user_integration_collaborator",
    "delete_user_integration_collaborator",
    "share_integration_with_group",
    "list_group_integration_collaborators",
    "update_group_integration_collaborator",
    "delete_group_integration_collaborator",
    "sweep",
    "NodeRow",
    "CustomScorer",
    "CustomizedChainPollScorer",
    "Dataset",
    "EvaluateSample",
    "EvaluateSamples",
    "PromptRow",
    "PromptRows",
    "RunTag",
    "ScorersConfiguration",
    "TemplateVersion",
    "Settings",
    "Models",
    "SupportedModels",
    "TagType",
    "Scorers",
    "EvaluateRun",
    "CustomizedScorerName",
    "Document",
    "Message",
    "MessageRole",
    "NodeType",
    "AgentStep",
    "LlmStep",
    "UserRole",
    "LlmStepAllowedIOType",
    "RetrieverStep",
    "RetrieverStepAllowedOutputType",
    "StepIOType",
    "StepWithChildren",
    "ToolStep",
    "WorkflowStep",
    "Workflows",
    "AuthMethod",
    "GetJobStatusResponse",
    "CreateUserResponse",
    "User",
    "__version__",
]

if is_langchain_available:
    from promptquality.callback import GalileoPromptCallback

    __all__.append("GalileoPromptCallback")
else:

    def __getattr__(name: str) -> None:
        if name == "GalileoPromptCallback":
            raise ImportError(
                "`GalileoPromptCallback` is a callback for `langchain` applications, but cannot be imported because "
                "`langchain-core` is not installed. If you want to use this callback, please install the dependency as "
                "`pip install langchain-core`."
            ) from None
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'") from None
