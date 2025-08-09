from typing import Optional

from pydantic import UUID4

from promptquality.constants.run import RunDefaults
from promptquality.types.config import PromptQualityConfig
from promptquality.types.run import GetJobStatusResponse
from promptquality.utils.logger import logger


def get_run_scorer_jobs(
    project_id: Optional[UUID4] = None, run_id: Optional[UUID4] = None
) -> list[GetJobStatusResponse]:
    config = PromptQualityConfig.get()
    project_id = project_id or config.current_project_id
    run_id = run_id or config.current_run_id
    if not project_id:
        raise ValueError("Project ID must be provided or set in config before getting run scorer jobs.")
    if not run_id:
        raise ValueError("Run ID must be provided or set in config before getting run scorer jobs.")
    logger.debug(f"Getting run scorer jobs for project {project_id}, run {run_id}...")
    response_dict = config.pq_api_client.get_run_scorer_jobs(project_id, run_id)
    jobs = [GetJobStatusResponse.model_validate(job) for job in response_dict]
    logger.debug(f"Got {len(jobs)} run scorer jobs for project {project_id}, run {run_id}.")
    return [job for job in jobs if job.job_name == RunDefaults.prompt_scorer_job_name]
