from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .client import ChatttsForgeClient, ChatttsForgeConnectionError, ChatttsForgeError
from .const import (
    CONF_AUDIO_FORMAT,
    CONF_BASE_URL,
    CONF_DEFAULT_LANGUAGE,
    CONF_MODEL,
    CONF_SPEAKER,
    CONF_STYLE,
    DEFAULT_AUDIO_FORMAT,
    DEFAULT_BASE_URL,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL,
    DEFAULT_NAME,
    DEFAULT_SPEAKER,
    DEFAULT_STYLE,
    DOMAIN,
)


def _build_schema(user_input: dict[str, Any] | None = None) -> vol.Schema:
    user_input = user_input or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=user_input.get(CONF_NAME, DEFAULT_NAME)): str,
            vol.Required(
                CONF_BASE_URL, default=user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL)
            ): str,
            vol.Required(
                CONF_SPEAKER, default=user_input.get(CONF_SPEAKER, DEFAULT_SPEAKER)
            ): str,
            vol.Required(CONF_STYLE, default=user_input.get(CONF_STYLE, DEFAULT_STYLE)): str,
            vol.Required(CONF_MODEL, default=user_input.get(CONF_MODEL, DEFAULT_MODEL)): str,
            vol.Required(
                CONF_AUDIO_FORMAT,
                default=user_input.get(CONF_AUDIO_FORMAT, DEFAULT_AUDIO_FORMAT),
            ): vol.In(["wav", "mp3", "raw"]),
            vol.Required(
                CONF_DEFAULT_LANGUAGE,
                default=user_input.get(CONF_DEFAULT_LANGUAGE, DEFAULT_LANGUAGE),
            ): str,
        }
    )


class ChatttsForgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            normalized_input = dict(user_input)
            normalized_input[CONF_BASE_URL] = normalized_input[CONF_BASE_URL].rstrip("/")

            await self.async_set_unique_id(normalized_input[CONF_BASE_URL])
            self._abort_if_unique_id_configured()

            client = ChatttsForgeClient(self.hass, normalized_input[CONF_BASE_URL])
            try:
                await client.async_validate()
            except ChatttsForgeConnectionError:
                errors["base"] = "cannot_connect"
            except ChatttsForgeError:
                errors["base"] = "invalid_response"
            except Exception:
                errors["base"] = "unknown"
            else:
                title = normalized_input[CONF_NAME]
                return self.async_create_entry(title=title, data=normalized_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(user_input),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        entry: config_entries.ConfigEntry,
    ) -> "ChatttsForgeOptionsFlow":
        return ChatttsForgeOptionsFlow(entry)


class ChatttsForgeOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            normalized_input = dict(user_input)
            normalized_input[CONF_BASE_URL] = normalized_input[CONF_BASE_URL].rstrip("/")

            client = ChatttsForgeClient(self.hass, normalized_input[CONF_BASE_URL])
            try:
                await client.async_validate()
            except ChatttsForgeConnectionError:
                errors["base"] = "cannot_connect"
            except ChatttsForgeError:
                errors["base"] = "invalid_response"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title="", data=normalized_input)

        merged = {**self.entry.data, **self.entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(merged),
            errors=errors,
        )
