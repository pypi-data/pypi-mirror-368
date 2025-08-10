"""Handles auth for Leviton Load Center."""

import asyncio
from contextlib import contextmanager
from datetime import datetime, timedelta
import logging
from typing import NamedTuple

from aiohttp import ClientResponse, ClientSession, ContentTypeError
from securelogging import LogRedactorMessage, add_secret, remove_secret

from .const import DEFAULT_HEADERS, MAX_RETRIES
from .errors import (
    ExceededMaximumRetries,
    InvalidAuth,
    InvalidResponse,
    UnknownAuthError,
)


@contextmanager
def passthrough():
    """Do nothing."""
    yield


class AuthData(NamedTuple):
    """Information related to the current Auth."""

    token: str
    userid: str
    expires: datetime


class LDATAAuth:
    """Handles auth-related information to Leviton API."""

    def __init__(self, username, password, hide_secrets: bool = False):
        """Initialize auth data."""
        self.logger = logging.getLogger(f"{__package__}[{username}]")
        self.username = username
        self.password = password
        self.auth_data: AuthData | None = None
        self._async_lock: asyncio.Lock = asyncio.Lock()
        if hide_secrets:
            self.secret_logger = LogRedactorMessage
        else:
            self.secret_logger = passthrough
        add_secret(password)
        with self.secret_logger():
            self.logger.info("Initializing connection for %s", username)

    @property
    def is_expired(self):
        """Determine if the current login data is expired."""
        if self.auth_data is None:
            return True
        return self.auth_data.expires <= datetime.now()

    async def token(self, client: ClientSession) -> str:
        """Get the auth token for making requests.

        If the token does not exist, perform the login to generate the token
        """
        if self.is_expired:
            await self.login(client)
        return self.auth_data.token

    async def userid(self, client: ClientSession) -> str:
        """Get the logged-in user for making request."""
        if self.is_expired:
            await self.login(client)
        return self.auth_data.userid

    async def login(self, client: ClientSession) -> AuthData:
        """Perform the login request."""
        async with self._async_lock:
            old_secrets = []
            if self.auth_data is not None:
                old_secrets = [self.auth_data.token, self.auth_data.userid]
            data = {"email": self.username, "password": self.password}
            retries = 0
            success = False
            while retries < MAX_RETRIES and not success:
                try:
                    async with client.post(
                        "https://my.leviton.com/api/Person/login?include=user",
                        headers=DEFAULT_HEADERS,
                        json=data,
                    ) as response:
                        self.auth_data = await self.process_login_response(response)
                        success = True
                except (InvalidResponse, UnknownAuthError):
                    retries += 1
                    await asyncio.sleep(1)
            if not success:
                raise ExceededMaximumRetries
            # Swap out the secrets
            add_secret(self.auth_data.token)
            add_secret(self.auth_data.userid)
            for secret in old_secrets:
                remove_secret(secret)
        return self.auth_data

    async def process_login_response(self, response: ClientResponse) -> AuthData:
        """Extract the pertinent information from the login response."""
        if response.status == 401:
            self.logger.warning("Invalid credentials provided")
            raise InvalidAuth
        if response.status != 200:
            self.logger.warning(
                "Unable to authenticate. Status Code: %s",
                response.status,
            )
            raise UnknownAuthError
        try:
            resp_json = await response.json()
        except (ValueError, ContentTypeError) as err:
            self.logger.exception("Unexpected data returned during token refresh")
            raise InvalidResponse from err
        created_dt = datetime.strptime(resp_json["created"], "%Y-%m-%dT%H:%M:%S.%fZ")
        auth_data = AuthData(
            token=resp_json["id"],
            userid=resp_json["userId"],
            expires=created_dt + timedelta(seconds=resp_json["ttl"]),
        )
        self.logger.info("Successfully authenticated to the API.")
        return auth_data
