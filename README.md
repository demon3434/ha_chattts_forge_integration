# ChatTTS Forge TTS for Home Assistant

这是一个用于 Home Assistant 的轻量级自定义 TTS 集成，用来通过界面接入自建的 `ChatTTS-Forge` 服务，不需要手写 YAML。

## 功能说明

- 通过 `设置 -> 设备与服务 -> 添加集成` 添加
- 使用你现有的 `ChatTTS-Forge` HTTP 服务作为后端
- 向 Home Assistant 提供可用于 `tts.speak` 的 TTS 实体
- 可在界面中配置后端地址和默认音色参数

## 支持内容

- 基于 UI 的配置流程
- 后续可通过选项页修改配置
- 可配置以下默认值：
  - 后端地址
  - 默认 speaker
  - 默认 style
  - 默认 model
  - 默认音频格式
  - 默认语言
- 支持在 `tts.speak` 调用时通过 `options` 覆盖默认参数

## 使用前提

你的 `ChatTTS-Forge` 后端服务需要先运行起来，并且 Home Assistant 能访问到它。

示例：

- `http://192.168.100.50:7870/docs`
- `http://192.168.100.50:7870/v1/models/list`

## 安装方式

把下面这个目录：

```text
custom_components/chattts_forge_tts
```

复制到 Home Assistant 配置目录中的：

```text
config/
└── custom_components/
    └── chattts_forge_tts/
```

然后重启 Home Assistant。

## 添加集成

在 Home Assistant 中进入：

`设置 -> 设备与服务 -> 添加集成`

搜索：

`ChatTTS Forge TTS`

建议初始填写：

- 名称：`ChatTTS Forge`
- 服务地址：`http://192.168.100.50:7870`
- 默认 speaker：`female2`
- 默认 style：`chat`
- 默认 model：`chat-tts`
- 默认音频格式：`wav`
- 默认语言：`zh-CN`

## 调用示例

```yaml
action: tts.speak
target:
  entity_id: tts.chattts_forge
data:
  media_player_entity_id: media_player.your_speaker
  message: 你好，这里是 Home Assistant 通过 ChatTTS Forge 的测试。
```

调用时覆盖默认参数：

```yaml
action: tts.speak
target:
  entity_id: tts.chattts_forge
data:
  media_player_entity_id: media_player.your_speaker
  message: 这是一段自定义音色测试。
  options:
    voice: female2
    style: chat
    model: chat-tts
    format: wav
```

## 说明

- 首次生成通常会比缓存命中慢很多
- 相同内容的重复请求，Home Assistant 的 TTS 缓存会显著加快返回速度
- 这个集成的目标是提供一个实用的 `ChatTTS-Forge` 接入桥接层，不负责完整的模型管理

## 目录结构

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
