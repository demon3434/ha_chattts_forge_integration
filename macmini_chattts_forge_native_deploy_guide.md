# Mac mini 原生部署 ChatTTS-Forge 指南

这份文档记录的是这次已经验证可用的部署方式，目标机器是：

- `Mac mini`
- IP：`192.168.100.50`
- 系统：`macOS 15.4.1`
- CPU：`Apple M4`
- 内存：`16 GB`

这次最终采用的是：

- `macOS 原生 Miniforge/conda`
- `ChatTTS-Forge` 裁剪为只保留 `chat-tts`
- `CPU` 推理
- 不接入 HA 之前，先单独验证服务可用

## 1. 为什么最终不用 Docker

Docker 路线试过，但不适合这台机器上的这份仓库：

- 仓库原始 `requirements.txt` 带了大量非 `ChatTTS` 必需依赖
- 里面还有 CUDA 版本 `torch/torchvision/torchaudio` 锁定
- 在 Apple Silicon 上继续走 Docker，构建和运行都不稳定

所以最终改成：

- 直接在 macOS 上创建 Python 环境
- 只保留 `ChatTTS` 所需链路

## 2. 先装基础环境

### 2.1 安装 Command Line Tools

```bash
sudo softwareupdate -i "Command Line Tools for Xcode-16.4" --verbose
```

### 2.2 安装 Miniforge

下载 `Miniforge3-MacOSX-arm64.sh` 后执行：

```bash
bash Miniforge3-MacOSX-arm64.sh -b -p "$HOME/miniforge3"
```

### 2.3 创建环境

```bash
$HOME/miniforge3/bin/conda create -y -n chatttsforge python=3.10 pip ffmpeg sox
```

### 2.4 安装 PyTorch

```bash
$HOME/miniforge3/bin/conda run -n chatttsforge pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0
```

## 3. 放置项目目录

最终可用目录是：

```text
/Users/yourname/chattts-forge-native
```

源码在：

```text
/Users/yourname/chattts-forge-native/app
```

如果重新部署，建议仍然使用这个目录，不要再放到 `~/docker/chattts-forge`。

## 4. 下载源码

在目标机上执行：

```bash
mkdir -p ~/chattts-forge-native
cd ~/chattts-forge-native
curl -L -o chattts-forge.zip https://github.com/lenML/Speech-AI-Forge/archive/refs/heads/main.zip
unzip chattts-forge.zip
mv Speech-AI-Forge-main app
rm -f chattts-forge.zip
```

## 5. 需要修改的源码

这次能跑通，关键不是“原样启动”，而是做了最小裁剪。

### 5.1 只保留 `chat-tts` 模型

需要修改：

- `modules/core/models/zoo/ModelZoo.py`

做法：

- 删除其他 TTS/STT/增强/变声模型的注册
- 只保留：
  - `chat-tts`

### 5.2 只保留 `ChatTTS` 推理流水线

需要修改：

- `modules/core/pipeline/factory.py`

做法：

- 只保留 `chat-tts` 的 pipeline
- 移除 `VoiceCloneProcessor`
- 移除 `EnhancerProcessor`
- 保留：
  - 文本归一化
  - style 合并
  - 基础音频后处理

### 5.3 只注册必要 API

需要修改：

- `modules/api/api_setup.py`

做法：

- 只保留：
  - `sys_api`
  - `models_api`
  - `style_api`
  - `speaker_api`
  - `tts_api`
  - `ssml_api`
- 不加载：
  - `openai_api`
  - `google_api`
  - `stt_api`
  - `vc_api`
  - 其他模型相关接口

### 5.4 macOS 上跳过 `wetext`

需要修改：

- `modules/core/tn/base_tn.py`

做法：

- 在 `wetext_normalize` 里让 macOS 直接返回，不走 `pynini/wetext`

核心逻辑：

```python
if os.name == "nt" or sys.platform == "darwin":
    return text
```

### 5.5 用轻量版音频工具

需要修改：

- `modules/utils/audio_utils.py`
- `modules/core/models/AudioReshaper.py`

做法：

- 避免一启动就强依赖 `librosa` / `pyrubberband`
- 改成按需导入
- 重采样用 `scipy.signal.resample_poly`

### 5.6 修复 `ChatTTS` 与当前 `transformers` 的缓存接口兼容问题

需要修改：

- `modules/repos_static/ChatTTS/ChatTTS/model/gpt.py`

做法：

- 修复 `DynamicCache` 没有 `get_max_length()` 的兼容问题
- 回退到 `get_seq_length()`

等价思路：

```python
max_cache_length = (
    past_key_values.get_max_length()
    if hasattr(past_key_values, "get_max_length")
    else past_key_values.get_seq_length()
)
```

### 5.7 强制走 CPU

这次实测中，Apple `MPS` 路径不稳定，会出现运行时报错。

因此最终做法是：

- 启动时固定 `CPU`
- 打开 `--no_half`

必要时可直接把设备选择逻辑钉死到 `cpu`。

## 6. 安装依赖

不要使用仓库原始的完整 `requirements.txt`。

应使用“只够 `chat-tts` 跑起来”的最小依赖集，核心包括：

- `fastapi`
- `uvicorn`
- `soundfile`
- `pydub`
- `numpy`
- `scipy`
- `transformers`
- `huggingface-hub`
- `vocos`
- `vector-quantize-pytorch`
- `pypinyin`
- `omegaconf`
- `pandas`
- `ftfy`
- `langdetect`
- `python-multipart`
- `psutil`
- `pybase16384`
- `numba`

如果是重新部署，建议按“这次已经整理好的最小依赖文件”安装，而不是直接照仓库原始依赖全装。

## 7. 下载模型

进入项目目录：

```bash
cd ~/chattts-forge-native/app
```

下载 `ChatTTS` 模型：

```bash
$HOME/miniforge3/bin/conda run -n chatttsforge python -m scripts.download_models --source huggingface --models chattts
```

模型会放到：

```text
models/ChatTTS
```

## 8. 启动服务

建议使用后台启动脚本，核心命令是：

```bash
$HOME/miniforge3/bin/conda run -n chatttsforge \
  python -u launch.py \
  --host 0.0.0.0 \
  --port 7870 \
  --use_cpu all \
  --no_half \
  --no_playground
```

当前机器上实际使用的启动脚本是：

```text
/Users/yourname/start_chattts.sh
```

服务目录：

```text
/Users/yourname/chattts-forge-native
```

日志：

```text
/Users/yourname/chattts-forge-native/native-chattts.log
```

## 9. 防火墙放行

如果 Mac 自带防火墙开着，需要放行这个 Python：

```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Users/yourname/miniforge3/envs/chatttsforge/bin/python
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /Users/yourname/miniforge3/envs/chatttsforge/bin/python
```

否则局域网内其他机器虽然能访问 `127.0.0.1:7870`，但访问 `192.168.100.50:7870` 会超时。

## 10. 验证接口

本机验证：

```bash
curl -I http://127.0.0.1:7870/docs
curl http://127.0.0.1:7870/v1/models/list
```

局域网验证：

- `http://192.168.100.50:7870/docs`
- `http://192.168.100.50:7870/v1/models/list`

## 11. 这次实测结果

当时实测大致结论：

- 短文本首轮生成：约 `18.9s`
- 短文本热启动生成：约 `9.0s`
- 长文本生成：约 `36s`

在 HA 里接入后再测：

- 10 秒左右音频，首次取回约 `17.7s`
- 29 秒左右音频，首次取回约 `49.9s`
- HA 缓存命中后再次取回几乎瞬时

结论：

- 短通知、短播报可用
- 长段朗读偏慢

## 12. 重新部署时最重要的经验

以后如果再次部署，优先记住这几条：

1. 不要再优先走 Docker。
2. 不要直接安装仓库原始完整依赖。
3. 不要保留多模型链路，只保留 `chat-tts`。
4. 不要走 `MPS`，先固定 `CPU`。
5. 别忘了放行 macOS 防火墙。
