from pathlib import Path
from posixpath import join
from typing import Any, Callable, Optional, Union

from pydantic import UUID4, BaseModel, HttpUrl, SecretStr
from requests import delete, get, post, put

from promptquality.constants.routes import Routes
from promptquality.types.chains.row import ChainIngestRequest
from promptquality.types.rows import GetRowsRequest
from promptquality.types.run import (
    CreateJobRequest,
    CreateProjectRequest,
    CreateRunRequest,
    CreateTemplateRequest,
    CreateTemplateVersionRequest,
    GetMetricsRequest,
    SelectTemplateVersionRequest,
    UploadDatasetRequest,
)
from promptquality.types.user_submitted_metrics import UserSubmittedMetrics
from promptquality.utils.request import HttpHeaders, make_request


class ApiClient(BaseModel):
    api_url: HttpUrl
    token: SecretStr

    @property
    def base_url(self) -> str:
        return self.api_url.unicode_string()

    @property
    def auth_header(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token.get_secret_value()}"}

    def _make_request(
        self,
        request_method: Callable,
        endpoint: str,
        body: Optional[dict] = None,
        data: Optional[dict] = None,
        files: Optional[dict] = None,
        params: Optional[dict] = None,
        timeout: Union[int, None] = None,
        json_request_only: bool = False,
        stream: bool = False,
    ) -> Any:
        if json_request_only:
            content_headers = HttpHeaders.accept_json()
        else:
            content_headers = HttpHeaders.json()
        headers = {**self.auth_header, **content_headers}
        return make_request(
            request_method=request_method,
            base_url=self.base_url,
            endpoint=endpoint,
            body=body,
            data=data,
            files=files,
            params=params,
            headers=headers,
            timeout=timeout,
            stream=stream,
        )

    def get_project_by_name(self, project_name: str) -> list[dict[str, str]]:
        return self._make_request(get, endpoint=Routes.projects, params=dict(project_name=project_name))

    def get_project(self, project_id: UUID4) -> dict[str, str]:
        return self._make_request(get, endpoint=Routes.project.format(project_id=project_id))

    def create_project(self, project_request: CreateProjectRequest) -> dict[str, str]:
        return self._make_request(post, endpoint=Routes.projects, body=project_request.model_dump())

    def create_template(self, template_request: CreateTemplateRequest) -> dict[str, str]:
        return self._make_request(
            post,
            endpoint=Routes.templates.format(project_id=template_request.project_id),
            body=template_request.model_dump(mode="json"),
        )

    def get_template(self, project_id: UUID4, template_id: UUID4) -> dict[str, str]:
        return self._make_request(get, endpoint=Routes.template.format(project_id=project_id, template_id=template_id))

    def get_template_version_by_name(
        self, project_id: UUID4, template_name: str, version: Optional[int] = None
    ) -> dict[str, str]:
        params: dict[str, Union[str, int]] = dict(template_name=template_name)
        if version is not None:
            params["version"] = version
        return self._make_request(get, endpoint=Routes.version_from_name.format(project_id=project_id), params=params)

    def get_templates(self, project_id: UUID4) -> list[dict[str, str]]:
        return self._make_request(get, endpoint=Routes.templates.format(project_id=project_id))

    def create_template_version(self, template_version_request: CreateTemplateVersionRequest) -> dict[str, str]:
        return self._make_request(
            post,
            endpoint=Routes.versions.format(
                project_id=template_version_request.project_id, template_id=template_version_request.template_id
            ),
            body=template_version_request.model_dump(mode="json", exclude_none=True),
        )

    def upload_dataset(self, dataset_request: UploadDatasetRequest) -> dict[str, str]:
        return self._make_request(
            post,
            json_request_only=True,
            endpoint=Routes.dataset.format(project_id=dataset_request.project_id),
            params=dataset_request.params,
            files=dataset_request.files,
        )

    def create_run(self, run_request: CreateRunRequest) -> dict[str, str]:
        return self._make_request(
            post,
            endpoint=Routes.runs.format(project_id=run_request.project_id),
            body=run_request.model_dump(mode="json"),
        )

    def get_run_by_name(self, project_id: UUID4, name: str) -> list[dict[str, str]]:
        return self._make_request(get, endpoint=Routes.runs.format(project_id=project_id), params=dict(run_name=name))

    def get_prompt_run(self, project_id: UUID4, run_id: UUID4) -> dict[str, str]:
        return self._make_request(get, endpoint=Routes.prompt_run.format(project_id=project_id, run_id=run_id))

    def create_job(self, job_request: CreateJobRequest) -> dict[str, str]:
        return self._make_request(
            post, endpoint=Routes.jobs, body=job_request.model_dump(mode="json", exclude_none=True)
        )

    def get_metrics(self, metrics_request: GetMetricsRequest) -> list[dict[str, Any]]:
        return self._make_request(get, endpoint=Routes.metrics.format(**metrics_request.model_dump(mode="json")))

    def get_rows(self, request: GetRowsRequest) -> list[dict[str, Any]]:
        return self._make_request(
            get, endpoint=Routes.rows.format(**request.model_dump(mode="json")), params=request.params()
        )

    def get_evaluate_samples(self, project_id: UUID4, run_id: UUID4) -> list[dict[str, Any]]:
        """
        Get the evaluate samples for a run in a project.

        Uses streaming to get the json lines response.
        """
        return self._make_request(
            get,
            endpoint=Routes.export_rows.format(project_id=project_id, run_id=run_id),
            params={"export_format": "jsonl"},
            stream=True,
        )

    def get_job_status(self, job_id: UUID4) -> dict[str, Any]:
        return self._make_request(get, endpoint=join(Routes.jobs, str(job_id)))

    def put_template_version_selection(self, select_version: SelectTemplateVersionRequest) -> dict[str, Any]:
        return self._make_request(
            put,
            endpoint=Routes.version.format(
                project_id=select_version.project_id,
                template_id=select_version.template_id,
                version=select_version.version,
            ),
        )

    def put_user_metrics(self, scores: UserSubmittedMetrics, project_id: UUID4, run_id: UUID4) -> dict[str, Any]:
        payload = scores.model_dump(mode="json", by_alias=True)
        return self._make_request(
            put, endpoint=Routes.user_submitted_metrics.format(project_id=project_id, run_id=run_id), body=payload
        )

    def register_scorer(self, scorer_name: str, scorer_file: Path) -> dict[str, Any]:
        return self._make_request(
            put,
            endpoint=Routes.registered_scorers,
            params=dict(name=scorer_name),
            files=dict(file=scorer_file.open("rb")),
            json_request_only=True,
        )

    def list_registered_scorers(self) -> list[dict[str, Any]]:
        return self._make_request(get, endpoint=Routes.registered_scorers)

    def delete_registered_scorer(self, registered_scorer_id: UUID4) -> dict[str, Any]:
        return self._make_request(
            delete, endpoint=Routes.registered_scorer.format(registered_scorer_id=registered_scorer_id)
        )

    def ingest_chain_rows(self, ingest_request: ChainIngestRequest, project_id: UUID4, run_id: UUID4) -> dict[str, Any]:
        return self._make_request(
            post,
            endpoint=Routes.chain_rows.format(project_id=project_id, run_id=run_id),
            body=ingest_request.model_dump(mode="json"),
        )

    def get_run_scorer_jobs(self, project_id: UUID4, run_id: UUID4) -> list[dict[str, Any]]:
        return self._make_request(get, endpoint=Routes.run_jobs.format(project_id=project_id, run_id=run_id))
