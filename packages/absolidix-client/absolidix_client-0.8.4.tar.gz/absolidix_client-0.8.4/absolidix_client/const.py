"""Constants for absolidix_client."""

from __future__ import annotations

import importlib.metadata
from logging import Logger, getLogger
from typing import Literal, Union

PROJECT_NAME = "absolidix_client"
PROJECT_VERSION = importlib.metadata.version(PROJECT_NAME)

# This is the default user agent,
# but it is adviced to use your own when building out your application
DEFAULT_USER_AGENT = f"absolidix_client/{PROJECT_VERSION}"


LOGGER: Logger = getLogger(PROJECT_NAME)

HttpMethods = Union[
    Literal["CONNECT"],
    Literal["HEAD"],
    Literal["GET"],
    Literal["DELETE"],
    Literal["OPTIONS"],
    Literal["PATCH"],
    Literal["POST"],
    Literal["PUT"],
    Literal["TRACE"],
]
