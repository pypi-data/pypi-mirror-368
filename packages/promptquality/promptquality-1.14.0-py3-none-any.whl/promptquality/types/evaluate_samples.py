from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EvaluateSample(BaseModel):
    """
    An evaluate sample or node in a workflow.

    For workflows, find sub nodes and their metadata in the children field.
    """

    index: int = Field(validation_alias="id")
    input: str
    output: str
    target: Optional[str] = None
    cost: Optional[float] = None
    children: list["EvaluateSample"] = Field(default_factory=list)
    model_config = ConfigDict(extra="allow")


class EvaluateSamples(BaseModel):
    """A collection of evaluate samples."""

    samples: list[EvaluateSample] = Field(default_factory=list)
