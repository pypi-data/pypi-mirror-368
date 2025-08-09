from itertools import product
from typing import Optional, Union

from tqdm.auto import tqdm

from promptquality.constants.models import Models
from promptquality.constants.scorers import Scorers
from promptquality.helpers import create_project
from promptquality.run_module import run
from promptquality.types.config import PromptQualityConfig
from promptquality.types.custom_scorer import CustomScorer
from promptquality.types.customized_scorer import CustomizedChainPollScorer
from promptquality.types.registered_scorers import RegisteredScorer
from promptquality.types.run import RunTag, ScorersConfiguration, TemplateVersion
from promptquality.types.settings import Settings
from promptquality.utils.dataset import DatasetType
from promptquality.utils.logger import logger


def create_settings_combinations(
    base_settings: Settings,
    model_aliases: Optional[list[Union[str, Models]]] = None,
    temperatures: Optional[list[float]] = None,
    max_token_options: Optional[list[int]] = None,
) -> list[Settings]:
    # Create all combinations of settings objects.
    alias_options: list[Optional[str]] = list(model_aliases) if model_aliases else [None]
    temperature_options: list[Optional[float]] = list(temperatures) if temperatures else [None]
    token_options: list[Optional[int]] = list(max_token_options) if max_token_options else [None]
    return [
        base_settings.model_copy(update=dict(model_alias=alias, temperature=temperature, max_tokens=tokens), deep=True)
        for alias, temperature, tokens in product(alias_options, temperature_options, token_options)
    ]


def run_sweep(
    templates: list[Union[str, TemplateVersion]],
    dataset: DatasetType,
    project_name: Optional[str] = None,
    model_aliases: Optional[list[Union[str, Models]]] = None,
    temperatures: Optional[list[float]] = None,
    settings: Optional[Settings] = None,
    max_token_options: Optional[list[int]] = None,
    scorers: Optional[list[Union[Scorers, CustomizedChainPollScorer, CustomScorer, RegisteredScorer, str]]] = None,
    generated_scorers: Optional[list[str]] = None,
    run_tags: Optional[list[RunTag]] = None,
    execute: bool = False,
    wait: bool = True,
    silent: bool = True,
    scorers_config: ScorersConfiguration = ScorersConfiguration(),
) -> None:
    """
    Run a sweep of prompt runs over various settings.

    We support optionally providing a subset of settings to override the base settings. If no settings are provided, we
    will use the base settings.
    """
    config = PromptQualityConfig.get()
    # Create project.
    project = create_project(project_name)
    settings = settings or Settings()

    all_settings = create_settings_combinations(settings, model_aliases, temperatures, max_token_options)
    all_combinations = list(product(templates, all_settings))
    if not execute:
        logger.warning(
            "⚠️ The `execute` flag is deprecated and ignored. All runs will be executed. Please remove this flag, as it will be removed in a future release."
        )
    print(f"Running batch with {len(all_combinations)} runs...")
    for template, settings in tqdm(all_combinations):
        run(
            template=template,
            dataset=dataset,
            project_name=project.name,
            settings=settings,
            scorers=scorers,
            generated_scorers=generated_scorers,
            run_tags=run_tags,
            wait=wait,
            silent=silent,
            scorers_config=scorers_config,
        )
    print(f"🔭 Batch runs created! View your prompt runs on the Galileo console at:  {config.project_url}.")
