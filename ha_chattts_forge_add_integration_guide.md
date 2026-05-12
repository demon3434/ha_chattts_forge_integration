# 在 Home Assistant 中添加 ChatTTS Forge 集成

这份说明只写“怎么添加”，不重复讲部署服务端。

前提：

- `ChatTTS-Forge` 已经在 `Mac mini` 上运行
- HA 可以访问：
  - `http://192.168.100.50:7870/docs`
  - `http://192.168.100.50:7870/v1/models/list`

## 1. 把集成放到 HA

把下面这个目录复制到 HA 的 `custom_components` 下：

```text
ha_chattts_forge_integration/custom_components/chattts_forge_tts
```

目标结构应为：

```text
config/custom_components/chattts_forge_tts
```

## 2. 重启 HA

复制完成后重启 Home Assistant。

## 3. 从界面添加

进入：

`设置 -> 设备与服务 -> 添加集成`

搜索：

`ChatTTS Forge TTS`

## 4. 推荐填写值

- 名称：`ChatTTS Forge`
- 服务地址：`http://192.168.100.50:7870`
- 默认音色：`female2`
- 默认 style：`chat`
- 默认模型：`chat-tts`
- 默认输出格式：`wav`
- 默认语言：`zh-CN`

保存后，HA 会创建：

```text
tts.chattts_forge
```

## 5. 测试

在 `开发者工具 -> 动作` 中测试：

```yaml
action: tts.speak
target:
  entity_id: tts.chattts_forge
data:
  media_player_entity_id: media_player.your_speaker
  message: 你好，这里是 Home Assistant 通过 ChatTTS Forge 的测试。
```

## 6. 如果只想验证，不想真播报

可以用 HA API 的 `tts_get_url` 路径，只生成 TTS 缓存，不触发真实播放器。

这样适合先验证：

- 集成是否正常加载
- 后端是否能生成音频
- 首次生成耗时是否能接受

## 7. 常见问题

### 1. 搜不到集成

一般是目录层级不对，确认：

```text
config/custom_components/chattts_forge_tts/manifest.json
```

### 2. 添加成功但不出音

先直接访问后端：

```text
http://192.168.100.50:7870/v1/tts?text=你好&spk=female2&style=chat&model=chat-tts&format=wav
```

### 3. 首次很慢，第二次很快

这是正常现象。

第一次：

- 需要真实生成音频

后续重复内容：

- HA 会命中 TTS 缓存

所以会快很多。
