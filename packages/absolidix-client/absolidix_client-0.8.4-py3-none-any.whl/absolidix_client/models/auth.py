"""Authenticators"""

from abc import abstractmethod
from asyncio import Lock, sleep

from aiohttp import ClientSession
from aiohttp.hdrs import METH_POST
from aiohttp.web_exceptions import HTTPTooManyRequests
from yarl import URL

from ..dtos import AbsolidixAuthCredentialsRequestDTO
from .base import AbsolidixBase


class BaseAuthenticator(AbsolidixBase):
    """Base authentication class"""

    lock: Lock

    def __init__(self):
        self.lock = Lock()

    @abstractmethod
    async def authenticate(self, session: ClientSession, base_url: URL) -> bool:
        "Run authentication procedure"

    @abstractmethod
    async def should_update(self, session: ClientSession, base_url: URL) -> bool:
        "Check if authentication needed"


class AbsolidixNoAuth(BaseAuthenticator):
    """No authentication (noop)"""

    async def authenticate(self, session: ClientSession, base_url: URL) -> bool:
        return True

    async def should_update(self, session: ClientSession, base_url: URL) -> bool:
        return False


class AbsolidixTokenAuth(BaseAuthenticator):
    """Token based authentication"""

    _token: str

    def __init__(self, token: str) -> None:
        super().__init__()
        self._token = token

    async def authenticate(self, session: ClientSession, base_url: URL) -> bool:
        session.headers["Authorization"] = f"Bearer {self._token}"
        return True

    async def should_update(self, session: ClientSession, base_url: URL) -> bool:
        return True


class AbsolidixLocalUserAuth(BaseAuthenticator):
    """Password based authentication"""

    endpoint = "v0/auth"
    _credentials: AbsolidixAuthCredentialsRequestDTO
    _cookie_name = "_sid"
    # force authentication in case when cookie already exists
    # in a session due to an unauthenticated request
    _force = True

    def __init__(self, email: str, password: str) -> None:
        super().__init__()
        self._credentials = AbsolidixAuthCredentialsRequestDTO(
            email=email, password=password
        )
        self.logger.warning(
            "Please, do NOT use password-based authentication, it is for testing only"
        )

    @classmethod
    def _get_cookie(cls, session: ClientSession, base_url: URL):
        return session.cookie_jar.filter_cookies(base_url).get(cls._cookie_name)

    async def authenticate(self, session: ClientSession, base_url: URL) -> bool:
        async with session.request(
            METH_POST,
            base_url / self.endpoint,
            json=self._credentials,
            raise_for_status=False,
        ) as resp:
            if resp.status == HTTPTooManyRequests.status_code:
                await sleep(10)
                return await self.authenticate(session, base_url)
            if not resp.ok:
                session.cookie_jar.clear(lambda x: x.key == self._cookie_name)
                return False
            self._force = False
            return bool(self._get_cookie(session, base_url))

    async def should_update(self, session: ClientSession, base_url: URL) -> bool:
        session.cookie_jar.update_cookies({}, base_url)
        return self._force or not bool(self._get_cookie(session, base_url))
