"""Ayla Networks API client for Noma iQ."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import (
    AC_OEM_MODELS,
    AYLA_ADS_URL,
    AYLA_USER_URL,
)

_LOGGER = logging.getLogger(__name__)


class NomaCantConnect(Exception):
    pass


class NomaInvalidAuth(Exception):
    pass


class NomaNoDevice(Exception):
    pass


class NomaIQApi:
    """Client for the Ayla Networks API."""

    def __init__(
        self,
        session: ClientSession,
        email: str,
        password: str,
        app_id: str,
        app_secret: str,
    ) -> None:
        self._session = session
        self._email = email
        self._password = password
        self._app_id = app_id
        self._app_secret = app_secret
        self._token: str | None = None

    async def authenticate(self) -> None:
        """Authenticate and store access token."""
        try:
            async with self._session.post(
                f"{AYLA_USER_URL}/users/sign_in.json",
                json={
                    "user": {
                        "email": self._email,
                        "password": self._password,
                        "application": {
                            "app_id": self._app_id,
                            "app_secret": self._app_secret,
                        },
                    }
                },
            ) as resp:
                if resp.status == 401:
                    raise NomaInvalidAuth
                resp.raise_for_status()
                data = await resp.json()
                self._token = data["access_token"]
        except ClientError as err:
            raise NomaCantConnect from err

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"auth_token {self._token}"}

    async def _get(self, url: str) -> Any:
        """GET with automatic re-auth on 401."""
        try:
            async with self._session.get(url, headers=self._headers) as resp:
                if resp.status == 401:
                    await self.authenticate()
                    async with self._session.get(url, headers=self._headers) as resp2:
                        resp2.raise_for_status()
                        return await resp2.json()
                resp.raise_for_status()
                return await resp.json()
        except ClientError as err:
            raise NomaCantConnect from err

    async def _post(self, url: str, payload: dict) -> None:
        """POST with automatic re-auth on 401."""
        try:
            async with self._session.post(url, headers=self._headers, json=payload) as resp:
                if resp.status == 401:
                    await self.authenticate()
                    async with self._session.post(url, headers=self._headers, json=payload) as resp2:
                        resp2.raise_for_status()
                        return
                resp.raise_for_status()
        except ClientError as err:
            raise NomaCantConnect from err

    async def get_ac_devices(self) -> list[dict[str, Any]]:
        """Return list of AC devices from Ayla."""
        data = await self._get(f"{AYLA_ADS_URL}/apiv1/devices.json")
        devices = [d["device"] for d in data]
        ac_devices = [d for d in devices if d.get("oem_model") in AC_OEM_MODELS]
        if not ac_devices:
            raise NomaNoDevice
        return ac_devices

    async def get_properties(self, dsn: str) -> dict[str, Any]:
        """Return all device properties as name→value dict."""
        data = await self._get(f"{AYLA_ADS_URL}/apiv1/dsns/{dsn}/properties.json")
        return {p["property"]["name"]: p["property"]["value"] for p in data}

    async def set_property(self, dsn: str, name: str, value: Any) -> None:
        """Set a device property via datapoint."""
        await self._post(
            f"{AYLA_ADS_URL}/apiv1/dsns/{dsn}/properties/{name}/datapoints.json",
            {"datapoint": {"value": value}},
        )
