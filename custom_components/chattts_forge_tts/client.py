from __future__ import annotations

from typing import Any

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util


class ChatttsForgeError(Exception):
    """Base client error."""


class ChatttsForgeConnectionError(ChatttsForgeError):
    """Raised when the backend is unreachable."""


class ChatttsForgeApiError(ChatttsForgeError):
    """Raised when the backend returns an invalid response."""


class ChatttsForgeClient:
    def __init__(self, hass: HomeAssistant, base_url: str) -> None:
        self.hass = hass
        self.base_url = base_url.rstrip("/")
        self.session = async_get_clientsession(hass)

    async def async_validate(self) -> dict[str, Any]:
        models = await self.async_fetch_models()
        speakers = await self.async_fetch_speakers()
        return {"models": models, "speakers": speakers, "checked_at": dt_util.utcnow()}

    async def async_fetch_models(self) -> list[str]:
        payload = await self._async_get_json("/v1/models/list")
        data = payload.get("data", [])
        if not isinstance(data, list):
            raise ChatttsForgeApiError("Invalid models response")
        return [str(item) for item in data]

    async def async_fetch_speakers(self) -> list[str]:
        payload = await self._async_get_json("/v1/speakers/list?limit=200&detailed=false")
        data = payload.get("data", {})
        items = data.get("items", []) if isinstance(data, dict) else []
        speakers: list[str] = []
        for item in items:
            try:
                name = item["data"]["meta"]["data"]["name"]
            except (KeyError, TypeError):
                continue
            if name:
                speakers.append(str(name))
        return speakers

    async def async_generate_tts(
        self,
        *,
        message: str,
        speaker: str,
        style: str,
        model: str,
        audio_format: str,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        seed: int | None = None,
    ) -> bytes:
        params: dict[str, Any] = {
            "text": message,
            "spk": speaker,
            "style": style,
            "model": model,
            "format": audio_format,
        }
        if temperature is not None:
            params["temperature"] = temperature
        if top_p is not None:
            params["top_p"] = top_p
        if top_k is not None:
            params["top_k"] = top_k
        if seed is not None:
            params["seed"] = seed

        try:
            async with self.session.get(
                f"{self.base_url}/v1/tts",
                params=params,
                timeout=120,
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise ChatttsForgeApiError(
                        f"TTS generation failed with status {response.status}: {text}"
                    )
                return await response.read()
        except ClientError as err:
            raise ChatttsForgeConnectionError(str(err)) from err

    async def _async_get_json(self, path: str) -> dict[str, Any]:
        try:
            async with self.session.get(f"{self.base_url}{path}", timeout=15) as response:
                if response.status != 200:
                    text = await response.text()
                    raise ChatttsForgeApiError(
                        f"Request failed with status {response.status}: {text}"
                    )
                payload = await response.json()
                if not isinstance(payload, dict):
                    raise ChatttsForgeApiError("Invalid JSON response")
                return payload
        except ClientError as err:
            raise ChatttsForgeConnectionError(str(err)) from err
