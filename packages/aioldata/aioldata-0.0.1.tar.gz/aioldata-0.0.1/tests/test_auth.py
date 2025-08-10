import datetime
import asyncio
import logging
import aiohttp
import securelogging
from aioresponses import aioresponses
import pytest
from aioldata import auth
from contextlib import asynccontextmanager

@pytest.fixture
def configured_auth():
    a = auth.LDATAAuth("user", "pass")
    a.auth_data = auth.AuthData(
        token="token",
        userid="userid",
        expires=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    )
    securelogging.add_secret("token")
    securelogging.add_secret("userid")
    return a


@pytest.fixture(autouse=True)
def reset_secrets():
    securelogging._called_from_test = True
    yield
    securelogging.reset_secrets()


class MockResponse:
    def __init__(self, data, status, has_bad_data=False):
        self._data = data
        self.has_bad_data = has_bad_data
        self.status = status

    async def json(self):
        if not self.has_bad_data:
            return self._data
        else:
            raise ValueError("bad json")

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


@pytest.mark.parametrize("hide_secrets", [True, False])
def test_LDATAAuth_ensure_no_password(hide_secrets, caplog):
    conf_auth = auth.LDATAAuth("user", "pass", hide_secrets=hide_secrets)
    with conf_auth.secret_logger():
        conf_auth.logger.warning("This is a cool pass")
    if hide_secrets:
        assert "pass" not in caplog.text
    else:
        assert "pass" in caplog.text

@pytest.mark.parametrize(
    ("auth_data", "expected"), [
        (
            None, True
        ),
        (
            auth.AuthData(
                token="token",
                userid="userid",
                expires=datetime.datetime.now() + datetime.timedelta(hours=1),
            ),
            False,
        ),
        (
            auth.AuthData(
                token="token",
                userid="userid",
                expires=datetime.datetime.now() - datetime.timedelta(hours=1),
            ),
            True,
        )
    ]
)
def test_is_expired(auth_data, expected, configured_auth):
    configured_auth.auth_data = auth_data
    assert configured_auth.is_expired == expected


@pytest.mark.asyncio
async def test_token():
    pass


@pytest.mark.asyncio
async def test_userid():
    pass


@pytest.mark.asyncio
async def test_login():
    pass


valid_login_response = MockResponse(
                {
                    "created": "2025-08-08T14:00:00.0000Z",
                    "ttl": 600,
                    "id": "12345",
                    "userId": "67890"
                },
                200
            )

valid_login_expected = auth.AuthData(
                token="12345",
                userid="67890",
                expires=datetime.datetime(2025, 8, 8, 14, 10),
            )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("response", "expected", "error", "messages"), [
        # Happy path
        (
            valid_login_response,
            valid_login_expected,
            None,
            ["Successfully authenticated to the API."],
        ),
        # Bad credentials
        (
            MockResponse([], 401), None, auth.InvalidAuth, ["Invalid credentials provided"]
        ),
        # Weird error code
        (
            MockResponse([], 201), None, auth.UnknownAuthError, ["Unable to authenticate. Status Code: 201"]
        ),
        # Bad JSON returned
        (
            MockResponse([], 200, has_bad_data=True), None, auth.InvalidResponse, ["Unexpected data returned during token refresh"]
        ),
    ]
)
async def test_process_login_response(response, expected, error, messages, caplog, configured_auth):
    caplog.set_level(logging.DEBUG)
    if not error:
        assert await configured_auth.process_login_response(response) == expected
    else:
        with pytest.raises(error):
            await configured_auth.process_login_response(response)
    if messages:
        for message in messages:
            assert message in caplog.text
