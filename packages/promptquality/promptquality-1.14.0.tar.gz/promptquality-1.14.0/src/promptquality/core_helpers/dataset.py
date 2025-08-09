from uuid import UUID

from galileo_core.helpers.dataset import create_dataset as core_create_dataset
from galileo_core.helpers.dataset import get_dataset_content as core_get_dataset_content
from galileo_core.helpers.dataset import list_datasets as core_list_datasets
from galileo_core.schemas.core.dataset import Dataset
from galileo_core.utils.dataset import DatasetType
from promptquality.types.config import PromptQualityConfig


def create_dataset(dataset: DatasetType) -> Dataset:
    config = PromptQualityConfig.get()
    return core_create_dataset(dataset=dataset, config=config)


def get_dataset_content(dataset_id: UUID) -> list[dict]:
    config = PromptQualityConfig.get()
    return core_get_dataset_content(dataset_id=dataset_id, config=config)


def list_datasets() -> list[Dataset]:
    config = PromptQualityConfig.get()
    return core_list_datasets(config=config)
