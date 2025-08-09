from io import BufferedReader
from pathlib import Path
from typing import Annotated, Optional

from pydantic import (
    UUID4,
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from promptquality.constants.dataset_format import DatasetFormat
from promptquality.constants.job import JobStatus
from promptquality.constants.run import RunDefaults, TagType
from promptquality.constants.scorers import Scorers
from promptquality.types.customized_scorer import CustomizedChainPollScorer
from promptquality.types.prompt_optimization import PromptOptimizationConfiguration
from promptquality.types.registered_scorers import RegisteredScorer
from promptquality.types.settings import Settings
from promptquality.utils.dataset import parse_dataset
from promptquality.utils.name import ts_name


class CreateProjectRequest(BaseModel):
    name: str
    type: str = RunDefaults.project_type

    @field_validator("name", mode="before")
    def generate_name(cls, value: Optional[str]) -> str:
        if not value:
            value = ts_name(prefix="project")
        return value


class TemplateVersion(BaseModel):
    name: str = Field(description="The name of the template")
    version: Optional[int] = Field(default=None, description="The template version, defaults to the production version")


class BaseTemplateVersionRequest(BaseModel):
    template: str
    version: Optional[int] = None


class CreateTemplateRequest(BaseTemplateVersionRequest):
    name: str
    project_id: UUID4

    @field_validator("name", mode="before")
    def generate_name(cls, value: Optional[str]) -> str:
        if not value:
            value = ts_name(prefix="template")
        return value


class CreateTemplateVersionRequest(BaseTemplateVersionRequest):
    template_id: UUID4
    project_id: UUID4


class BaseTemplateVersionResponse(BaseTemplateVersionRequest):
    id: UUID4


class CreateTemplateVersionResponse(BaseTemplateVersionResponse):
    version: int


class BaseTemplateResponse(BaseModel):
    id: UUID4
    name: str
    template: str
    selected_version: CreateTemplateVersionResponse
    selected_version_id: UUID4
    all_versions: list[CreateTemplateVersionResponse] = Field(default_factory=list)


class BaseDatasetRequest(BaseModel):
    format: DatasetFormat = DatasetFormat.csv
    file_path: Path = Field(exclude=True)

    @model_validator(mode="before")
    def dataset_to_path(cls, values: dict) -> dict:
        if "file_path" in values:
            values["file_path"], values["format"] = parse_dataset(values["file_path"])
        return values

    @property
    def files(self) -> dict[str, BufferedReader]:
        return dict(file=self.file_path.open("rb"))


class UploadDatasetRequest(BaseDatasetRequest):
    project_id: UUID4
    prompt_template_version_id: UUID4
    file_path: Path = Field(exclude=True)

    @property
    def params(self) -> dict[str, str]:
        return dict(prompt_template_version_id=str(self.prompt_template_version_id), format=self.format.value)


class Dataset(BaseModel):
    id: UUID4 = Field(validation_alias=AliasChoices("dataset_id", "id"))
    file_name: Optional[str] = None
    num_rows: Optional[int] = None


class RunTag(BaseModel):
    key: Annotated[str, StringConstraints(max_length=256)]
    value: Annotated[str, StringConstraints(max_length=256)]
    tag_type: TagType


class CreateRunRequest(BaseModel):
    name: str
    project_id: UUID4
    task_type: int = RunDefaults.prompt_evaluation_task_type
    run_tags: list[RunTag] = Field(default_factory=list)

    @field_validator("name", mode="before")
    def generate_name(cls, value: Optional[str]) -> str:
        if not value:
            value = ts_name(prefix="run")
        return value


class RunResponse(CreateRunRequest):
    id: UUID4


class PromptRunResponse(RunResponse):
    template_id: Optional[UUID4] = None
    dataset_id: Optional[UUID4] = None
    template_version_id: Optional[UUID4] = None
    template_version: Optional[int] = None
    template_version_selected: Optional[bool] = None
    total_responses: int = 0
    prompt_settings: Optional[Settings] = None


class ProjectResponse(CreateProjectRequest):
    id: UUID4
    runs: list[RunResponse] = Field(default_factory=list)


class ScorerSettings(BaseModel):
    scorer_name: str


class ScorersConfiguration(BaseModel):
    """
    Configuration to control which scorers to enable and disable.

    Can be used in runs and chain runs, with or instead of scorers arg. scorers explicitly set in scorers arg will
    override this.
    """

    adherence_nli: bool = False
    chunk_attribution_utilization_gpt: bool = False
    chunk_attribution_utilization_nli: bool = False
    completeness_gpt: bool = False
    completeness_nli: bool = False
    context_relevance: bool = False
    factuality: bool = False
    groundedness: bool = False
    instruction_adherence: bool = False
    ground_truth_adherence: bool = False
    tool_selection_quality: bool = False
    pii: bool = False
    prompt_injection: bool = False
    prompt_injection_gpt: bool = False
    prompt_perplexity: bool = False
    input_sexist: bool = False
    input_sexist_gpt: bool = False
    sexist: bool = False
    sexist_gpt: bool = False
    tone: bool = False
    tool_error_rate: bool = False
    # TODO why no input toxicity existing here currently?
    input_toxicity: bool = False
    input_toxicity_gpt: bool = False
    toxicity: bool = False
    toxicity_gpt: bool = False
    agentic_session_success: bool = False
    agentic_workflow_success: bool = False

    @model_validator(mode="after")
    def disallow_conflicts(self) -> "ScorersConfiguration":
        """Raise Value Error if conflicting scorers are selected."""
        source = None
        if self.adherence_nli and self.groundedness:
            source = "adherence"
        elif self.chunk_attribution_utilization_gpt and self.chunk_attribution_utilization_nli:
            source = "attribution/utilization"
        elif self.completeness_gpt and self.completeness_nli:
            source = "completeness"
        elif self.input_sexist_gpt and self.input_sexist:
            source = "input sexist"
        elif self.sexist_gpt and self.sexist:
            source = "sexist"
        elif self.input_toxicity_gpt and self.input_toxicity:
            source = "input toxicity"
        elif self.toxicity_gpt and self.toxicity:
            source = "toxicity"
        elif self.prompt_injection_gpt and self.prompt_injection:
            source = "prompt injection"
        if source:
            raise ValueError(f"Cannot use Luna {source} with Plus {source}")
        return self

    @classmethod
    def from_scorers(cls, scorers: list[Scorers]) -> "ScorersConfiguration":
        return cls(**{scorer.value: True for scorer in scorers})

    def merge_scorers(self, scorers: list[Scorers]) -> "ScorersConfiguration":
        return self.model_copy(update={scorer.value: True for scorer in scorers})


class CreateJobRequest(BaseModel):
    project_id: UUID4
    run_id: UUID4
    dataset_id: Optional[UUID4] = None
    prompt_template_version_id: Optional[UUID4] = None
    prompt_settings: Optional[Settings] = None
    prompt_scorers_configuration: Optional[ScorersConfiguration] = None
    prompt_scorer_settings: Optional[ScorerSettings] = None
    prompt_registered_scorers_configuration: Optional[list[RegisteredScorer]] = None
    prompt_generated_scorers_configuration: Optional[list[str]] = None
    prompt_customized_scorers_configuration: Optional[list[CustomizedChainPollScorer]] = None
    job_name: str = RunDefaults.prompt_run_job_name
    task_type: Optional[int] = RunDefaults.prompt_evaluation_task_type
    prompt_optimization_configuration: Optional[PromptOptimizationConfiguration] = None


class JobInfoMixin(BaseModel):
    job_id: UUID4
    link: str
    job_name: Optional[str] = None


class CreateJobResponse(CreateJobRequest, JobInfoMixin): ...


class GetMetricsRequest(BaseModel):
    project_id: UUID4
    run_id: UUID4


class PromptMetrics(BaseModel):
    total_responses: Optional[int] = None
    average_hallucination: Optional[float] = None
    average_bleu: Optional[float] = None
    average_rouge: Optional[float] = None
    average_cost: Optional[float] = None
    total_cost: Optional[float] = None

    model_config = ConfigDict(extra="allow")


class GetJobStatusResponse(BaseModel):
    id: UUID4
    project_id: UUID4
    run_id: UUID4
    status: JobStatus
    job_name: str = RunDefaults.prompt_run_job_name
    error_message: Optional[str] = None
    progress_message: Optional[str] = None
    steps_completed: int = 0
    steps_total: int = 0
    progress_percent: float = 0.0
    request_data: Optional[CreateJobRequest] = None


class AzureModelDeployment(BaseModel):
    model: str = Field(description="The name of the model.")
    id: str = Field(description="The ID of the deployment.")

    model_config = ConfigDict(
        # Avoid Pydantic's protected namespace warning since we want to use
        # `model_name` as a field name since that matches what the Azure API uses.
        protected_namespaces=()
    )


class SelectTemplateVersionRequest(BaseModel):
    project_id: UUID4
    template_id: UUID4
    version: int


class UserSubmittedMetricsResponse(BaseModel):
    project_id: UUID4
    run_id: UUID4
    job_id: UUID4
    scorer_name: str
