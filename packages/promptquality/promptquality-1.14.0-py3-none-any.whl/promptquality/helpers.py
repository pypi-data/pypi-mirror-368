from typing import Optional, Union
from uuid import UUID

from pydantic import UUID4

from galileo_core.schemas.shared.scorers.base_configs import GeneratedScorerConfig
from promptquality.constants.prompt_optimization import PromptOptimizationDefaults
from promptquality.constants.run import RunDefaults
from promptquality.get_rows_module import get_rows
from promptquality.types.chains.row import ChainIngestRequest, ChainIngestResponse, NodeRow
from promptquality.types.config import PromptQualityConfig
from promptquality.types.custom_scorer import CustomScorer
from promptquality.types.customized_scorer import CustomizedChainPollScorer
from promptquality.types.prompt_optimization import PromptOptimizationConfiguration
from promptquality.types.registered_scorers import RegisteredScorer
from promptquality.types.run import (
    BaseTemplateResponse,
    CreateJobRequest,
    CreateJobResponse,
    CreateProjectRequest,
    CreateRunRequest,
    CreateTemplateRequest,
    CreateTemplateVersionRequest,
    CreateTemplateVersionResponse,
    Dataset,
    GetJobStatusResponse,
    ProjectResponse,
    PromptRunResponse,
    RunResponse,
    RunTag,
    ScorersConfiguration,
    SelectTemplateVersionRequest,
    TemplateVersion,
    UploadDatasetRequest,
    UserSubmittedMetricsResponse,
)
from promptquality.types.settings import Settings
from promptquality.types.user_submitted_metrics import UserSubmittedMetrics
from promptquality.utils.dataset import DatasetType
from promptquality.utils.logger import logger


def create_project(project_name: Optional[str] = None) -> ProjectResponse:
    config = PromptQualityConfig.get()
    project_request = CreateProjectRequest(name=project_name)
    existing_project = get_project_from_name(project_request.name, raise_if_missing=False)
    if existing_project:
        logger.info(f"Project {project_request.name} already exists, using it.")
        project_response = existing_project
    else:
        logger.debug(f"Creating project {project_request.name}...")
        response_dict = config.pq_api_client.create_project(project_request)
        project_response = ProjectResponse.model_validate(response_dict)
        logger.debug(f"Created project with name {project_response.name}, ID {project_response.id}.")
    config.merge_project(project_response)
    return project_response


def get_project(project_id: UUID4) -> ProjectResponse:
    config = PromptQualityConfig.get()
    response_dict = config.pq_api_client.get_project(project_id)
    project = ProjectResponse.model_validate(response_dict)
    logger.debug(f"Got project with name {project.name}, ID {project.id}.")
    config.merge_project(project)
    return project


def get_project_from_name(project_name: str, raise_if_missing: bool = True) -> Optional[ProjectResponse]:
    """
    Get a project by name.

    Parameters
    ----------
    project_name : str
        Name of the project.
    raise_if_missing : bool
        Whether to raise an error if the project is missing.

    Returns
    -------
    Optional[ProjectResponse]
        Project object.
    """
    config = PromptQualityConfig.get()
    projects = [
        ProjectResponse.model_validate(proj)
        for proj in config.pq_api_client.get_project_by_name(project_name=project_name)
    ]
    if raise_if_missing and len(projects) == 0:
        raise ValueError(f"Project {project_name} does not exist.")
    elif len(projects) > 0:
        project_response = projects[0]
        logger.debug(f"Got project with name {project_response.name}, with ID {project_response.id}.")
        config.merge_project(project_response)
        return project_response
    else:
        return None


def create_template(
    template: str, project_id: Optional[UUID4] = None, template_name: Optional[str] = None
) -> BaseTemplateResponse:
    """
    Create a template in the project.

    If the project ID is not provided, it will be taken from the config.

    If a template with the same name already exists, it will be used. If the template
    text is the same, the existing template version will be selected. Otherwise, a new
    template version will be created and selected.

    Parameters
    ----------
    template : str
        Template text to use for the new template.
    project_id : Optional[UUID4], optional
        Project ID, by default None, i.e. use the current project ID in config.
    template_name : Optional[str], optional
        Name for the template, by default None, i.e. use a random name.
    config : Optional[Config], optional
        PromptQuality Configuration, by default None, i.e. use the current config on
        disk.

    Returns
    -------
    BaseTemplateResponse
        Validated response from the API.

    Raises
    ------
    ValueError
        If the project ID is not set in config.
    """
    config = PromptQualityConfig.get()
    project_id = project_id or config.current_project_id
    if not project_id:
        raise ValueError("Project ID must be provided or set in config to create a template.")
    template_request = CreateTemplateRequest(template=template, project_id=project_id, name=template_name)
    existing_templates = {template.name: template for template in get_templates(project_id)}
    if template_request.name in existing_templates:
        existing_template_response = existing_templates[template_request.name]
        logger.debug(
            f"Template {template_request.name} already exists, using it. "
            f"Template ID is {existing_template_response.id}."
        )
        existing_template_text = {
            template_version.template: template_version for template_version in existing_template_response.all_versions
        }
        if template_request.template in existing_template_text:
            logger.debug(f"Template text for template {template_request.name} already exists, selecting it.")
            template_version = existing_template_text[template_request.template]
        else:
            logger.debug("Creating template version for template {existing_template_response.id}...")
            template_version = create_template_version(
                template_request.template, template_id=existing_template_response.id, project_id=project_id
            )
        template_response = select_template_version(template_version.version, project_id, existing_template_response.id)
    else:
        logger.debug(f"Creating template {template_request.name}...")
        response_dict = config.pq_api_client.create_template(template_request)
        template_response = BaseTemplateResponse.model_validate(response_dict)
    config.merge_template(template_response)
    logger.debug(f"Created template with name {template_response.name}, ID {template_response.id}.")
    return template_response


def get_template_from_id(
    project_id: Optional[UUID4] = None, template_id: Optional[UUID4] = None
) -> BaseTemplateResponse:
    config = PromptQualityConfig.get()
    project_id = project_id or config.current_project_id
    template_id = template_id or config.current_template_id
    if not project_id:
        raise ValueError("Project ID must be provided or set in config to get the template.")
    if not template_id:
        raise ValueError("Template ID must be provided or set in config to get the template.")
    logger.debug(f"Getting template for {project_id=} and {template_id=}...")
    return BaseTemplateResponse.model_validate(
        config.pq_api_client.get_template(project_id=project_id, template_id=template_id)
    )


def get_template_version_from_name(
    template_version: TemplateVersion, project_id: Optional[UUID4] = None
) -> CreateTemplateVersionResponse:
    config = PromptQualityConfig.get()
    project_id = project_id or config.current_project_id
    if not project_id:
        raise ValueError("Project ID must be provided or set in config to get the template.")
    logger.debug(
        f"Getting template version {template_version.version} for project {project_id} and template {template_version.name}..."
    )
    template_version_response = config.pq_api_client.get_template_version_by_name(
        project_id, template_version.name, template_version.version
    )
    return CreateTemplateVersionResponse.model_validate(template_version_response)


def get_templates(project_id: Optional[UUID4] = None) -> list[BaseTemplateResponse]:
    config = PromptQualityConfig.get()
    project_id = project_id or config.current_project_id
    if not project_id:
        raise ValueError("Project ID must be provided or set in config to get the templates.")
    logger.debug(f"Getting all templates for {project_id=}...")
    return [
        BaseTemplateResponse.model_validate(template)
        for template in config.pq_api_client.get_templates(project_id=project_id)
    ]


def select_template_version(
    version: int, project_id: Optional[UUID4] = None, template_id: Optional[UUID4] = None
) -> BaseTemplateResponse:
    config = PromptQualityConfig.get()
    project_id = project_id or config.current_project_id
    template_id = template_id or config.current_template_id
    if not project_id:
        raise ValueError("Project ID must be provided or set in config to select a different template version.")
    if not template_id:
        raise ValueError("Template ID must be provided or set in config to select a different template version.")

    template_version_request = SelectTemplateVersionRequest(
        project_id=project_id, template_id=template_id, version=version
    )
    logger.debug(
        f"Selecting template version {template_version_request.version} for "
        f"template ID {template_version_request.template_id}..."
    )
    response_dict = config.pq_api_client.put_template_version_selection(template_version_request)
    template_response = BaseTemplateResponse.model_validate(response_dict)
    config.merge_template(template_response)
    logger.debug(
        f"Selected template version with ID {template_response.selected_version_id}, "
        f"version {template_response.selected_version} for template ID "
        f"{template_response.selected_version_id}."
    )
    return template_response


def create_template_version(
    template: str,
    project_id: Optional[UUID4] = None,
    template_id: Optional[UUID4] = None,
    version: Optional[int] = None,
) -> CreateTemplateVersionResponse:
    """
    Create a template version for the current template ID in config.

    Parameters
    ----------
    template : str
        Template text to use for the new template version.
    project_id : Optional[UUID4], optional
        Project ID, by default None, i.e. use the current project ID in config.
    template_id : Optional[UUID4], optional
        Template ID, by default None, i.e. use the current template ID in config.
    version : Optional[int], optional
        Version number, by default None, i.e. use the next version number.
    config : Optional[Config], optional
        PromptQuality Configuration, by default None, i.e. use the current config on
        disk.

    Returns
    -------
    CreateTemplateVersionResponse
        Validated response from the API.

    Raises
    ------
    ValueError
        If the template ID is not set in config.
    ValueError
        If the project ID is not set in config.
    """
    config = PromptQualityConfig.get()
    project_id = project_id or config.current_project_id
    template_id = template_id or config.current_template_id
    if not project_id:
        raise ValueError("Project ID must be provided or set in config before creating template version.")
    if not template_id:
        raise ValueError("Template ID must be provided or set in config before creating template version.")
    version_request = CreateTemplateVersionRequest(
        template=template, version=version, project_id=project_id, template_id=template_id
    )
    logger.debug("Creating template version for template ID {version_request.template_id}...")
    response_dict = config.pq_api_client.create_template_version(version_request)
    version_response = CreateTemplateVersionResponse.model_validate(response_dict)
    config.merge_template_version(version_response)
    logger.debug(f"Created template version with ID {version_response.id}, version {version_response.version}.")
    return version_response


def upload_dataset(dataset: Union[UUID4, DatasetType], project_id: UUID4, template_version_id: UUID4) -> UUID4:
    config = PromptQualityConfig.get()
    if isinstance(dataset, UUID):
        logger.debug("UUID passed for dataset.")
        return dataset

    dataset_request = UploadDatasetRequest(
        project_id=project_id, prompt_template_version_id=template_version_id, file_path=dataset
    )
    logger.debug(f"Uploading dataset {dataset_request.file_path}...")
    response_dict = config.pq_api_client.upload_dataset(dataset_request)
    dataset_response = Dataset.model_validate(response_dict)
    config.merge_dataset(dataset_response)
    logger.debug(f"Uploaded dataset with ID {dataset_response.id}.")
    return dataset_response.id


def create_run(
    project_id: UUID4,
    run_name: Optional[str] = None,
    task_type: int = RunDefaults.prompt_evaluation_task_type,
    run_tags: Optional[list[RunTag]] = None,
) -> UUID4:
    config = PromptQualityConfig.get()
    run_tags = run_tags or list()
    run_request = CreateRunRequest(name=run_name, project_id=project_id, task_type=task_type, run_tags=run_tags)
    logger.debug(f"Creating run {run_request.name}...")
    response_dict = config.pq_api_client.create_run(run_request)
    run_response = RunResponse.model_validate(response_dict)
    config.merge_run(run_response)
    logger.debug(f"Created run with name {run_request.name}, ID {run_response.id}.")
    return run_response.id


def get_run_from_name(run_name: str, project_id: Optional[UUID4] = None) -> RunResponse:
    """
    Retrieve a run by name.

    Parameters
    ----------
    run_name : str
        Name of the run.
    project_id : Optional[UUID4]
        ID of the project.
    config : Optional[Config]
        Config object.
    Returns
    -------
    RunResponse
        Run object.
    """
    config = PromptQualityConfig.get()
    project_id = project_id or config.current_project_id
    if not project_id:
        raise ValueError("Project ID must be provided or set in config to get the run.")
    runs = [
        RunResponse.model_validate(run)
        for run in config.pq_api_client.get_run_by_name(project_id=project_id, name=run_name)
    ]
    if runs:
        run_response = runs[0]
        logger.debug(f"Got run with name {run_response.name}, with ID {run_response.id}.")
        config.merge_run(run_response)
        return run_response
    else:
        raise ValueError(f"Run {run_name} does not exist.")


def get_run_settings(
    run_name: Optional[str] = None, run_id: Optional[UUID4] = None, project_id: Optional[UUID4] = None
) -> Optional[Settings]:
    """
    Retrieves the prompt settings for a given run. Can pass either run_name or run_id. If both are passed, run_id will
    be used.

    Parameters
    ----------
    run_name : Optional[str]
        Name of the run.
    run_id : Optional[UUID4]
        ID of the run.
    project_id : Optional[UUID4]
        ID of the project.
    config : Optional[Config]
        Config object.
    Returns
    -------
    Optional[Settings]
        Prompt settings for the run.
    """
    config = PromptQualityConfig.get()
    project_id = project_id or config.current_project_id
    if not project_id:
        raise ValueError("Project ID must be provided or set in config to get the run.")
    if run_id is not None:
        pass
    elif run_name is not None:
        run_id = get_run_from_name(run_name, project_id).id
    else:
        run_id = config.current_run_id
    if not run_id:
        raise ValueError("Run ID or run name must be provided or set in config to get the run settings.")
    run = PromptRunResponse.model_validate(config.pq_api_client.get_prompt_run(project_id, run_id))
    return run.prompt_settings


def create_job(
    project_id: Optional[UUID4] = None,
    run_id: Optional[UUID4] = None,
    dataset_id: Optional[UUID4] = None,
    template_version_id: Optional[UUID4] = None,
    settings: Optional[Settings] = None,
    scorers_config: ScorersConfiguration = ScorersConfiguration(),
    registered_scorers: Optional[list[RegisteredScorer]] = None,
    generated_scorers: Optional[list[str]] = None,
    customized_scorers: Optional[list[CustomizedChainPollScorer]] = None,
) -> UUID4:
    config = PromptQualityConfig.get()
    project_id = project_id or config.current_project_id
    run_id = run_id or config.current_run_id
    template_version_id = template_version_id or config.current_template_version_id
    if not project_id:
        raise ValueError("Project ID must be provided or set in config before creating job.")
    if not run_id:
        raise ValueError("Run ID must be provided or set in config before creating job.")
    if not template_version_id:
        raise ValueError("Template version ID must be provided or set in config before creating job.")
    job_request = CreateJobRequest(
        project_id=project_id,
        run_id=run_id,
        dataset_id=dataset_id,
        prompt_settings=settings,
        prompt_scorers_configuration=scorers_config,
        prompt_registered_scorers_configuration=registered_scorers,
        prompt_generated_scorers_configuration=generated_scorers,
        prompt_customized_scorers_configuration=customized_scorers,
        prompt_template_version_id=template_version_id,
    )
    logger.debug("Creating job...")
    response_dict = config.pq_api_client.create_job(job_request)
    job_response = CreateJobResponse.model_validate(response_dict)
    config.merge_job(job_response)
    logger.debug(f"Created job with ID {job_response.job_id}.")
    return job_response.job_id


def create_prompt_optimization_job(
    prompt_optimization_configuration: PromptOptimizationConfiguration,
    project_id: UUID4,
    run_id: UUID4,
    train_dataset_id: UUID4,
) -> UUID4:
    """
    Kicks off a prompt optimization job in Runners.

    Parameters
    ----------
    prompt_optimization_config : PromptOptimizationConfiguration
        Configuration for the prompt optimization job.
    project_name : str
        Name of the project, by default None. If None we will generate a name.
    run_name : str
        Name of the run, by default None. If None we will generate a name.
    config : Config
        pq config object, by default None. If None we will use the default config.

    Returns
    -------
    job_id: UUID
        Job ID kicked off for prompt optimization
    """
    job_request = CreateJobRequest(
        project_id=project_id,
        run_id=run_id,
        dataset_id=train_dataset_id,
        job_name=PromptOptimizationDefaults.prompt_optimization_job_name,
        prompt_optimization_configuration=prompt_optimization_configuration,
    )
    config = PromptQualityConfig.get()
    logger.debug("Creating job...")
    response_dict = config.pq_api_client.create_job(job_request)
    job_response = CreateJobResponse.model_validate(response_dict)
    config.merge_job(job_response)
    logger.debug(f"Created job with ID {job_response.job_id}.")
    return job_response.job_id


def get_job_status(job_id: Optional[UUID4] = None) -> GetJobStatusResponse:
    config = PromptQualityConfig.get()
    logger.debug(f"Getting job status for job {job_id}...")
    job_id = job_id or config.current_job_id
    if not job_id:
        raise ValueError("job_id must be provided")
    response_dict = config.pq_api_client.get_job_status(job_id)
    job_status_response = GetJobStatusResponse.model_validate(response_dict)
    logger.debug(
        f"Got job status for job {job_id}, status is "
        f"{job_status_response.progress_message}, "
        f"{job_status_response.progress_percent} percentage."
    )
    return job_status_response


def upload_custom_metrics(
    custom_scorer: CustomScorer,
    project_id: Optional[UUID4] = None,
    run_id: Optional[UUID4] = None,
    task_type: Optional[int] = None,
) -> UserSubmittedMetricsResponse:
    config = PromptQualityConfig.get()
    project_id = project_id or config.current_project_id
    run_id = run_id or config.current_run_id
    if not project_id:
        raise ValueError("Project ID must be provided or set in config before uploading custom metrics.")
    if not run_id:
        raise ValueError("Run ID must be provided or set in config before uploading custom metrics.")
    prompt_rows = get_rows(project_id, run_id, task_type)
    scores = UserSubmittedMetrics.from_scorer(custom_scorer, prompt_rows)
    logger.debug(f"Uploading custom scores for {custom_scorer.name}...")
    response_dict = config.pq_api_client.put_user_metrics(scores, project_id, run_id)
    upload_metrics_response = UserSubmittedMetricsResponse.model_validate(response_dict)
    logger.debug(f"Uploaded custom scores for {custom_scorer.name} with job ID {upload_metrics_response.job_id}.")
    return upload_metrics_response


def ingest_chain_rows(
    rows: list[NodeRow],
    project_id: Optional[UUID4] = None,
    run_id: Optional[UUID4] = None,
    scorers_config: ScorersConfiguration = ScorersConfiguration(),
    registered_scorers: Optional[list[RegisteredScorer]] = None,
    generated_scorers: Optional[list[GeneratedScorerConfig]] = None,
    customized_scorers: Optional[list[CustomizedChainPollScorer]] = None,
) -> ChainIngestResponse:
    config = PromptQualityConfig.get()
    project_id = project_id or config.current_project_id
    run_id = run_id or config.current_run_id
    if not project_id:
        raise ValueError("Project ID must be provided or set in config before ingesting chain rows.")
    if not run_id:
        raise ValueError("Run ID must be provided or set in config before ingesting chain rows.")
    ingest_request = ChainIngestRequest(
        rows=rows,
        prompt_scorers_configuration=scorers_config,
        prompt_registered_scorers_configuration=registered_scorers,
        generated_scorers=generated_scorers,
        prompt_customized_scorers_configuration=customized_scorers,
    )
    logger.debug(f"Ingesting chain rows for project {project_id}, run {run_id}...")
    response_dict = config.pq_api_client.ingest_chain_rows(ingest_request, project_id, run_id)
    chain_ingest_response = ChainIngestResponse.model_validate(response_dict)
    config.merge_job(chain_ingest_response)
    logger.debug(
        f"Ingested chain rows for project {project_id}, run {run_id}, with {chain_ingest_response.num_rows} rows."
    )
    return chain_ingest_response
