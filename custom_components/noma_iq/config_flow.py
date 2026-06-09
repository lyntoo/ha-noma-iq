"""Config flow for Noma iQ."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NomaCantConnect, NomaInvalidAuth, NomaNoDevice, NomaIQApi
from .const import CONF_APP_ID, CONF_APP_SECRET, DOMAIN


class NomaIQConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle config flow for Noma iQ."""

    VERSION = 1

    _devices: list[dict] = []
    _email: str = ""
    _password: str = ""
    _app_id: str = ""
    _app_secret: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]
            app_id = user_input[CONF_APP_ID]
            app_secret = user_input[CONF_APP_SECRET]
            api = NomaIQApi(
                async_get_clientsession(self.hass),
                email,
                password,
                app_id,
                app_secret,
            )
            try:
                await api.authenticate()
                devices = await api.get_ac_devices()
            except NomaInvalidAuth:
                errors["base"] = "invalid_auth"
            except NomaCantConnect:
                errors["base"] = "cannot_connect"
            except NomaNoDevice:
                errors["base"] = "no_device"
            else:
                self._email = email
                self._password = password
                self._app_id = app_id
                self._app_secret = app_secret
                if len(devices) == 1:
                    return self._create_entry(devices[0])
                self._devices = devices
                return await self.async_step_select_device()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_APP_ID): str,
                    vol.Required(CONF_APP_SECRET): str,
                }
            ),
            errors=errors,
        )

    async def async_step_select_device(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            dsn = user_input["dsn"]
            device = next(d for d in self._devices if d["dsn"] == dsn)
            return self._create_entry(device)

        options = {d["dsn"]: f"{d.get('product_name', d['dsn'])} ({d['dsn']})" for d in self._devices}
        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema({vol.Required("dsn"): vol.In(options)}),
        )

    def _create_entry(self, device: dict) -> ConfigFlowResult:
        dsn = device["dsn"]
        name = device.get("product_name") or device.get("oem_model") or dsn
        return self.async_create_entry(
            title=name,
            data={
                CONF_EMAIL: self._email,
                CONF_PASSWORD: self._password,
                CONF_APP_ID: self._app_id,
                CONF_APP_SECRET: self._app_secret,
                "dsn": dsn,
                "model": device.get("oem_model", ""),
            },
        )
