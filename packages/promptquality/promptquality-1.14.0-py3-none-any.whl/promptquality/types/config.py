# mypy: disable-error-code=syntax
# We need to ignore syntax errors until https://github.com/python/mypy/issues/17535 is resolved.
from posixpath import join
from typing import Any, Optional

from pydantic import UUID4

from galileo_core.schemas.base_config import GalileoConfig
from promptquality.constants.prompt_optimization import PromptOptimizationDefaults
from promptquality.constants.run import RunDefaults
from promptquality.types.run import (
    BaseTemplateResponse,
    CreateTemplateVersionResponse,
    Dataset,
    JobInfoMixin,
    ProjectResponse,
    RunResponse,
)
from promptquality.utils.api_client import ApiClient
from promptquality.utils.logger import logger


class PromptQualityConfig(GalileoConfig):
    config_filename: str = "pq-config.json"
    # Project.
    current_project_id: Optional[UUID4] = None
    current_project_name: Optional[str] = None
    # Run.
    current_run_id: Optional[UUID4] = None
    current_run_name: Optional[str] = None
    current_run_url: Optional[str] = None
    current_run_task_type: Optional[int] = None
    # Template.
    current_template_id: Optional[UUID4] = None
    current_template_name: Optional[str] = None
    # Version
    current_template_version_id: Optional[UUID4] = None
    current_template_version: Optional[int] = None
    current_template: Optional[str] = None
    # Dataset.
    current_dataset_id: Optional[UUID4] = None
    # Job.
    current_job_id: Optional[UUID4] = None
    current_prompt_optimization_job_id: Optional[UUID4] = None

    @classmethod
    def get(cls, **kwargs: Any) -> "PromptQualityConfig":
        """
        Get the config object from the global variable or set it if it's not already set from the kwargs or environment
        variables.
        """
        global _pq_config
        # Ignore the type here because we know that _config is an object of the BaseConfig class or its sub-classes.
        _pq_config = cls._get(_pq_config, **kwargs)  # type: ignore[arg-type]
        return _pq_config

    @property
    def project_url(self) -> str:
        if not self.current_project_id:
            raise ValueError("No project set.")
        return join(
            self.console_url.unicode_string(),
            "prompt",
            "chains" if self.current_run_task_type == RunDefaults.prompt_chain_task_type else "",
            f"{self.current_project_id}",
        )

    @property
    def pq_api_client(self) -> ApiClient:
        if not self.validated_api_client:
            raise ValueError("No token set. Please log in.")
        return ApiClient(api_url=self.validated_api_client.host, token=self.validated_api_client.jwt_token)

    def reset(self) -> None:
        self.current_project_id = None
        self.current_project_name = None
        self.current_run_id = None
        self.current_run_name = None
        self.current_run_task_type = None
        self.current_template_id = None
        self.current_template_name = None
        self.current_template_version_id = None
        self.current_template_version = None
        self.current_template = None
        self.current_dataset_id = None
        self.current_job_id = None
        self.current_prompt_optimization_job_id = None
        super().reset()

    def logout(self) -> None:
        self.write()
        print("👋 You have logged out of 🔭 Galileo.")

    def merge_project(self, project: ProjectResponse) -> None:
        self.current_project_id = project.id
        self.current_project_name = project.name
        self.write()
        logger.debug(f"📝 Set current project to {project.name}.")

    def merge_template(self, template: BaseTemplateResponse) -> None:
        self.current_template_id = template.id
        self.current_template_name = template.name
        self.merge_template_version(template.selected_version)
        self.write()
        logger.debug(f"📝 Set current template to {template.name}.")

    def merge_template_version(self, template_version: CreateTemplateVersionResponse) -> None:
        self.current_template_version_id = template_version.id
        self.current_template_version = template_version.version
        self.current_template = template_version.template
        self.write()
        logger.debug(f"📝 Set current template version to {template_version.version}.")

    def merge_dataset(self, dataset: Dataset) -> None:
        self.current_dataset_id = dataset.id
        self.write()
        logger.debug(f"📝 Set current dataset to {dataset.id}.")

    def merge_run(self, run: RunResponse) -> None:
        self.current_run_id = run.id
        self.current_run_name = run.name
        self.current_run_task_type = run.task_type
        self.write()
        logger.debug(f"📝 Set current run to {run.name}.")

    def merge_job(self, job_info: JobInfoMixin) -> None:
        self.current_job_id = job_info.job_id
        self.current_run_url = job_info.link
        if job_info.job_name == PromptOptimizationDefaults.prompt_optimization_job_name:
            self.current_prompt_optimization_job_id = job_info.job_id
        self.write()
        logger.debug(f"📝 Set current job to {job_info.job_id}.")


_pq_config: Optional[PromptQualityConfig] = None
