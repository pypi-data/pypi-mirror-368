"""Base class for all GitHub objects."""

from logging import Logger

from ..const import LOGGER


class AbsolidixBase:
    """Base class for all Absolidix objects."""

    logger: Logger = LOGGER
