"""Gathers data from Leviton API."""

__all__ = ["LDATAConnector", "Residence"]

import asyncio
from collections.abc import Generator
from contextlib import asynccontextmanager, contextmanager
import logging
from typing import NamedTuple

import aiohttp
from aiohttp import web_exceptions
from securelogging import LogRedactorMessage

from .auth import InvalidAuth, LDATAAuth
from .const import DEFAULT_HEADERS, MAX_RETRIES
from .errors import ExceededMaximumRetries, InvalidResidences
from .parser import PanelData, parse_data


class Residence(NamedTuple):
    """Data related to a single residence."""

    access: str
    status: str
    person_id: str
    residence_id: int
    residental_account_id: int
    id: int


@contextmanager
def passthrough():
    """Do nothing."""
    yield


class LDATAConnector:
    """Handles communication with Leviton API."""

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession | None = None,
        hide_secrets: bool = True,
        three_phase: bool = False,
    ):
        """Initialize the data connector."""
        self.logger = logging.getLogger(f"{__package__}[{username}]")
        self._auth = LDATAAuth(username, password, hide_secrets=hide_secrets)
        self._three_phase = three_phase
        self._web_session = session
        self._close_session = session is None
        self._residences: list[Residence] = []
        if hide_secrets:
            self.secret_logger = LogRedactorMessage
        else:
            self.secret_logger = passthrough
        if not session:
            connector = aiohttp.TCPConnector(
                limit_per_host=3,
            )
            self._web_session = aiohttp.ClientSession(connector=connector)

    async def get_headers(self):
        """Get default headers for an API call."""
        headers: dict[str, str] = {**DEFAULT_HEADERS}
        headers["authorization"] = await self._auth.token(self._web_session)
        return headers

    async def _get_residence_information(self) -> list[Residence]:
        """Query Leviton API for all available residences."""
        acct_id = await self._auth.userid(self._web_session)
        url = f"https://my.leviton.com/api/Person/{acct_id}/residentialPermissions"
        res = await self.request(
            "GET",
            url,
        )
        res.raise_for_status()
        data = await res.json()
        if len(data) == 0:
            raise InvalidAuth("No accounts present")
        residences = []
        for elem in data:
            if "residentialAccountId" not in elem:
                continue
            residences.append(
                Residence(
                    access=elem["access"],
                    status=elem["status"],
                    person_id=elem["personId"],
                    residence_id=elem["residenceId"],
                    residental_account_id=elem["residentialAccountId"],
                    id=elem["id"],
                )
            )
        if len(residences) == 0:
            self.logger.warning("Unable to gather residence information")
            raise InvalidResidences
        if residences[0].residence_id is None:
            residence_id = await self.get_primary_residence(
                residences[0].residental_account_id
            )
            residences[0] = Residence(
                access=residences[0].access,
                status=residences[0].status,
                person_id=residences[0].person_id,
                residence_id=residence_id,
                residental_account_id=residences[0].residental_account_id,
                id=residences[0].id,
            )
        self._residences = residences
        return self._residences

    async def get_primary_residence(self, res_account_id: int) -> int:
        """Lookup the primary residence ID."""
        url = f"https://my.leviton.com/api/ResidentialAccounts/{res_account_id}"
        res = await self.request(
            "GET",
            url,
        )
        res.raise_for_status()
        return (await res.json())["primaryResidenceId"]

    async def residental_account_id(self) -> int:
        """Get the account ID for the given credentials."""
        if len(self._residences) == 0:
            await self._get_residence_information()
        return self._residences[0].residentialAccountId

    async def residences(self) -> list[int]:
        """Get a list of residences' IDs for the given credentials."""
        if len(self._residences) == 0:
            await self._get_residence_information()
        return self._residences

    @asynccontextmanager
    async def create_request(
        self, method: str, url: str, **kwargs
    ) -> Generator[aiohttp.ClientResponse, None, None]:
        """Make a request to any path with V2 request method (auth in header).

        Returns a generator with aiohttp ClientResponse.
        """
        headers = await self.get_headers()
        headers.update(kwargs.get("headers", {}))
        kwargs["headers"] = headers
        kwargs["ssl"] = True
        async with self._web_session.request(method, url, **kwargs) as res:
            yield res

    async def request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make request on the api and return response data."""
        retries = 0
        with self.secret_logger():
            self.logger.info("Making request [%s] to %s with %s", method, url, kwargs)
        while retries < MAX_RETRIES:
            retries += 1
            if retries > 1:
                retry_wait = 0.25 * retries
                await asyncio.sleep(retry_wait)
            async with self.create_request(method, url, **kwargs) as resp:
                # 503 means the service is temporarily unavailable, back off a bit.
                # 429 means the bridge is rate limiting/overloaded, we should back off a bit.
                if resp.status in [429, 503]:
                    continue
                # 403 is bad auth
                if resp.status == 403:
                    raise web_exceptions.HTTPForbidden
                await resp.read()
                return resp
        raise ExceededMaximumRetries("Exceeded maximum number of retries")

    async def status(self) -> PanelData:
        """Get the current information for the given panels."""
        api_data = []
        api_data.extend(await self.get_ldata_panels())
        api_data.extend(await self.get_whems_panels())
        return parse_data(api_data, self._three_phase)

    async def get_ldata_panels(self) -> list[dict]:
        """Get all LDATA Panels."""
        all_panels = []
        headers = {"filter": '{"include":["residentialBreakers"]}'}
        for residence in await self.residences():
            url = f"https://my.leviton.com/api/Residences/{residence.residence_id}/residentialBreakerPanels"
            res = await self.request("GET", url, headers=headers)
            for panel in await res.json():
                panel["ModuleType"] = "LDATA"
                all_panels.append(panel)
                self.logger.debug("Panels for %s: %s", residence.residence_id, panel)
        return all_panels

    async def get_whems_panels(self) -> list[dict]:
        """Get all WHEMS IOT Panels."""
        all_panels: list = []
        for residence in await self.residences():
            url = f"https://my.leviton.com/api/Residences/{residence.residence_id}/iotWhems"
            res = await self.request("GET", url)
            for panel in await res.json():
                panel["ModuleType"] = "WHEMS"
                # Make the data look like an LDATA module
                panel["rmsVoltage"] = panel["rmsVoltageA"]
                panel["rmsVoltage2"] = panel["rmsVoltageB"]
                panel["updateVersion"] = panel["version"]
                panel["residentialBreakers"] = await self.get_whems_breakers(
                    panel["id"]
                )
                panel["CTs"] = await self.get_whems_ct(panel["id"])
                all_panels.append(panel)
            self.logger.debug("Panels for %s: %s", residence.residence_id, all_panels)
        return all_panels

    async def get_whems_breakers(self, panel_id: str) -> list[dict]:
        """Get all WHEMS IOT Breakers for the given panel."""
        headers = {
            "filter": "{}",
        }
        url = f"https://my.leviton.com/api/IotWhems/{panel_id}/residentialBreakers"
        res = await self.request("GET", url, headers=headers)
        return await res.json()

    async def get_whems_ct(self, panel_id: str) -> list[dict]:
        """Get all WHEMS IOT CTs for the given panel."""
        headers = {
            "filter": "{}",
        }
        url = f"https://my.leviton.com/api/IotWhems/{panel_id}/iotCts"
        res = await self.request("GET", url, headers=headers)
        return await res.json()

    async def _set_breaker_power(
        self, breaker_id: str, enabled: bool
    ) -> aiohttp.ClientResponse:
        """Set the power state for a given breaker."""
        headers = {
            "referer": f"https://my.leviton.com/home/residential-breakers/{breaker_id}/settings"
        }
        return self.request(
            "POST",
            f"https://my.leviton.com/api/ResidentialBreakers/{breaker_id}",
            json={"remoteOn": enabled},
            headers=headers,
        )

    async def _set_breaker_trip(
        self, breaker_id: str, enabled: bool
    ) -> aiohttp.ClientResponse:
        """Set the trip state for a given breaker."""
        headers = {
            "referer": f"https://my.leviton.com/home/residential-breakers/{breaker_id}/settings"
        }
        return self.request(
            "POST",
            f"https://my.leviton.com/api/ResidentialBreakers/{breaker_id}",
            json={"remoteTrip": enabled},
            headers=headers,
        )

    async def remote_on(self, breaker_id: str) -> aiohttp.ClientResponse:
        """Turn on the given breaker."""
        return self._set_breaker_power(breaker_id, True)

    async def remote_off(self, breaker_id: str) -> aiohttp.ClientResponse:
        """Turn off the given breaker."""
        return self._set_breaker_power(breaker_id, False)

    async def remote_trip(self, breaker_id: str) -> aiohttp.ClientResponse:
        """Trip the given breaker."""
        return self._set_breaker_trip(breaker_id, True)

    async def remote_reset(self, breaker_id: str) -> aiohttp.ClientResponse:
        """Reset (untrip) the given breaker."""
        return self._set_breaker_trip(breaker_id, False)
