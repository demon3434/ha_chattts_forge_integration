# ChatTTS Forge TTS for Home Assistant

A lightweight Home Assistant custom TTS integration for connecting a self-hosted `ChatTTS-Forge` service through the UI, without editing YAML.

## What It Does

- Adds a Home Assistant TTS integration through `Settings -> Devices & Services -> Add Integration`
- Uses your existing `ChatTTS-Forge` HTTP service as the backend
- Exposes a TTS provider that works with `tts.speak`
- Lets you configure the backend URL and default voice settings in the UI

## Features

- UI-based config flow
- Options flow for updating settings later
- Configurable:
  - backend URL
  - default speaker
  - default style
  - default model
  - default audio format
  - default language
- Supports runtime `options` overrides in `tts.speak`

## Requirements

Your `ChatTTS-Forge` backend must already be running and reachable from Home Assistant.

Example:

- `http://192.168.100.50:7870/docs`
- `http://192.168.100.50:7870/v1/models/list`

## Installation

Copy this directory:

```text
custom_components/chattts_forge_tts
```

into your Home Assistant config directory:

```text
config/
└── custom_components/
    └── chattts_forge_tts/
```

Then restart Home Assistant.

## Add the Integration

In Home Assistant:

`Settings -> Devices & Services -> Add Integration`

Search for:

`ChatTTS Forge TTS`

Recommended initial values:

- Name: `ChatTTS Forge`
- Service URL: `http://192.168.100.50:7870`
- Default speaker: `female2`
- Default style: `chat`
- Default model: `chat-tts`
- Default audio format: `wav`
- Default language: `zh-CN`

## Example Usage

```yaml
action: tts.speak
target:
  entity_id: tts.chattts_forge
data:
  media_player_entity_id: media_player.your_speaker
  message: Hello, this is a ChatTTS Forge test from Home Assistant.
```

Override defaults at call time:

```yaml
action: tts.speak
target:
  entity_id: tts.chattts_forge
data:
  media_player_entity_id: media_player.your_speaker
  message: This is a custom voice test.
  options:
    voice: female2
    style: chat
    model: chat-tts
    format: wav
```

## Notes

- First-time generation is slower than cached playback
- Repeated requests for the same content can be served much faster by Home Assistant's TTS cache
- This integration focuses on a practical `ChatTTS-Forge` bridge, not on full model management

## Repository Layout

```text
custom_components/chattts_forge_tts/
├── __init__.py
├── client.py
├── config_flow.py
├── const.py
├── manifest.json
├── strings.json
├── translations/
│   ├── en.json
│   └── zh-Hans.json
└── tts.py
```
