from __future__ import annotations

from typing import Any

from homeassistant.components.tts import TextToSpeechEntity, TtsAudioType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .client import ChatttsForgeClient
from .const import (
    CONF_AUDIO_FORMAT,
    CONF_DEFAULT_LANGUAGE,
    CONF_MODEL,
    CONF_SPEAKER,
    CONF_STYLE,
    DEFAULT_AUDIO_FORMAT,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL,
    DEFAULT_NAME,
    DEFAULT_SPEAKER,
    DEFAULT_STYLE,
    DOMAIN,
    OPTION_FORMAT,
    OPTION_MODEL,
    OPTION_SEED,
    OPTION_SPEAKER,
    OPTION_STYLE,
    OPTION_TEMPERATURE,
    OPTION_TOP_K,
    OPTION_TOP_P,
    OPTION_VOICE,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ChatttsForgeTTSEntity(hass, entry)])


class ChatttsForgeTTSEntity(TextToSpeechEntity):
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._entry_data = hass.data[DOMAIN][entry.entry_id]
        self._client: ChatttsForgeClient = self._entry_data["client"]

        merged = {**entry.data, **entry.options}
        self._name = merged.get(CONF_NAME, DEFAULT_NAME)
        self._speaker = merged.get(CONF_SPEAKER, DEFAULT_SPEAKER)
        self._style = merged.get(CONF_STYLE, DEFAULT_STYLE)
        self._model = merged.get(CONF_MODEL, DEFAULT_MODEL)
        self._audio_format = merged.get(CONF_AUDIO_FORMAT, DEFAULT_AUDIO_FORMAT)
        self._default_language = merged.get(CONF_DEFAULT_LANGUAGE, DEFAULT_LANGUAGE)

        self._attr_name = self._name
        self._attr_unique_id = f"{entry.entry_id}_tts"
        self._attr_supported_languages = ["zh-CN", "zh", "en-US", "en"]
        self._attr_default_language = self._default_language
        self._attr_supported_options = [
            OPTION_VOICE,
            OPTION_SPEAKER,
            OPTION_STYLE,
            OPTION_MODEL,
            OPTION_FORMAT,
            OPTION_TEMPERATURE,
            OPTION_TOP_P,
            OPTION_TOP_K,
            OPTION_SEED,
        ]
        self._attr_default_options = {
            OPTION_VOICE: self._speaker,
            OPTION_SPEAKER: self._speaker,
            OPTION_STYLE: self._style,
            OPTION_MODEL: self._model,
            OPTION_FORMAT: self._audio_format,
        }

    @callback
    def async_get_supported_voices(self, language: str) -> list[str] | None:
        return self._entry_data.get("speakers") or None

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        speaker = (
            options.get(OPTION_VOICE)
            or options.get(OPTION_SPEAKER)
            or self._speaker
        )
        style = options.get(OPTION_STYLE, self._style)
        model = options.get(OPTION_MODEL, self._model)
        audio_format = options.get(OPTION_FORMAT, self._audio_format)
        temperature = options.get(OPTION_TEMPERATURE)
        top_p = options.get(OPTION_TOP_P)
        top_k = options.get(OPTION_TOP_K)
        seed = options.get(OPTION_SEED)

        audio = await self._client.async_generate_tts(
            message=message,
            speaker=speaker,
            style=style,
            model=model,
            audio_format=audio_format,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            seed=seed,
        )
        return audio_format, audio
