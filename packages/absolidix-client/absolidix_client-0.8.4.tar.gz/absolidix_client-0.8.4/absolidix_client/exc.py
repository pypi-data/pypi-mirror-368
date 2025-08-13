"""Custom exceptions for absolidix_client."""

from typing import Optional


class AbsolidixException(BaseException):
    """
    This is raised when unknown exceptions occour.
    And it's used as a base for all other exceptions
    so if you want to catch all Absolidix related errors
    you should catch this base exception.
    """


class AbsolidixConnectionException(AbsolidixException):
    """This is raised when there is a connection issue with Absolidix."""


class AbsolidixError(AbsolidixException):
    """Base of all errors based on results"""

    status: int = 0
    message: Optional[str]

    def __init__(
        self,
        *args: object,
        status: Optional[int],
        message: Optional[str] = None,
    ):
        super().__init__(*args)
        if status:
            self.status = status
        if message:
            self.message = message

    def __str__(self) -> str:
        return f"status: {self.status}, message: {self.message}"


class AbsolidixNotFoundException(AbsolidixError):
    """This is raised when the requested resource is not found."""


class AbsolidixPayloadException(AbsolidixError):
    """This is raised when the payload is invalid."""


class AbsolidixPermissionException(AbsolidixError):
    """This is raised when the user has no permission to do the requested resource."""


class AbsolidixAuthenticationException(AbsolidixError):
    """This is raised when we recieve an authentication issue."""


class AbsolidixQuotaException(AbsolidixError):
    """This is raised when quota excided."""


class AbsolidixAsyncRuntimeWarning(UserWarning):
    """Use of sync API in async runtime"""
