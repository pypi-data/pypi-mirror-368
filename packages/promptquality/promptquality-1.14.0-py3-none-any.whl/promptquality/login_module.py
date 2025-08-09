from os import environ
from typing import Any, Optional

from promptquality.types.config import PromptQualityConfig
from promptquality.utils.logger import logger


def login(console_url: Optional[str] = None, **kwargs: Any) -> PromptQualityConfig:
    """
    Login to Galileo.

    By default, this will login to the Galileo Console (set as environemnt variable or passed as an argument) using the
    credentials provided in the environment variables GALILEO_USERNAME and GALILEO_PASSWORD or GALILEO_API_KEY. If the
    credentials are not provided in the environment variables, they can be passed in as keyword arguments (username and
    password or api_key).

    This function is optional and only required if you want to login using args that are not set as environment variables.
    """
    if console_url:
        if environ.get("GALILEO_CONSOLE_URL") == console_url:
            logger.warning(
                "The console URL provided is the same as the one in the environment variable GALILEO_CONSOLE_URL and is not required to be passed in."
            )
        kwargs["console_url"] = console_url
    return PromptQualityConfig.get(**kwargs)
