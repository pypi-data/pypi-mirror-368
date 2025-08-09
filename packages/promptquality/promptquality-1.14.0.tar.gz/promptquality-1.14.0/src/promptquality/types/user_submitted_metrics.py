from typing import Any

from pydantic import BaseModel, Field, model_validator
from tqdm.auto import tqdm

from promptquality.types.custom_scorer import CustomMetricType, CustomScorer
from promptquality.types.rows import PromptRow
from promptquality.utils.logger import logger


class UserSubmittedMetrics(BaseModel):
    scorer_name: str = "_user_submitted"
    name: str = Field(serialization_alias="metric_name")

    scores: list[CustomMetricType] = Field(default_factory=list)
    indices: list[int] = Field(default_factory=list)

    aggregates: dict[str, CustomMetricType] = Field(default_factory=dict)

    @model_validator(mode="before")
    def validate_scores_and_indices(cls, values: dict[str, Any]) -> dict[str, Any]:
        if len(values["scores"]) != len(values["indices"]):
            raise ValueError("Length of scores must match length of indices.")
        return values

    @classmethod
    def from_scorer(cls, scorer: CustomScorer, prompt_rows: list[PromptRow]) -> "UserSubmittedMetrics":
        scores, indices = [], []
        for i, row in enumerate(tqdm(prompt_rows, desc=f"Running {scorer.name} metric")):
            try:
                score = scorer.scorer_fn(row)
                scores.append(score)
                indices.append(row.index)
            except Exception as exception:
                logger.warning(
                    f"Failed to score response: {row.response} at index {i}, exception:{exception}. Skipping row {i}."
                )
        if scorer.aggregator_fn:
            aggregates = scorer.aggregator_fn(scores, indices)
        else:
            logger.debug(f"No aggregator set for scorer {scorer.name}.")
            aggregates = dict()
        return cls(name=scorer.name, scores=scores, indices=indices, aggregates=aggregates)
