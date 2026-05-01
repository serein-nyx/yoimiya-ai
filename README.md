# 宵宫 AI · Yoimiya AI

> 一个运行在本地的语音对话程序，用麦克风说话，她用宵宫的人格回应你。
>
> A local voice chat program. Speak into your mic — she responds as Yoimiya.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue" />
  <img src="https://img.shields.io/badge/Whisper-medium-green" />
  <img src="https://img.shields.io/badge/LLM-Doubao-orange" />
  <img src="https://img.shields.io/badge/TTS-Volcengine-red" />
  <img src="https://img.shields.io/badge/CUDA-13.x-76b900" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" />
</p>

---

## 它能做什么 · What it does

按下回车，对着麦克风说话，再按回车结束。程序会：

1. 用本地 Whisper（GPU 加速）把你的话转成文字
2. 把文字发给豆包大模型，用宵宫的人格生成回复
3. 用火山引擎语音合成把回复念出来

支持多轮对话，宵宫记得你们之前说过的话。

Press Enter, speak into your mic, press Enter again to stop. The program will:

1. Transcribe your speech locally with Whisper (GPU-accelerated)
2. Send the text to Doubao LLM, which responds in Yoimiya's character
3. Synthesize the reply with Volcengine TTS and play it back

Multi-turn conversation is supported — Yoimiya remembers what you've said.

---

## 技术架构 · Architecture

```
麦克风 / Mic
    │
    ▼
faster-whisper (medium, CUDA float16)   ← 本地运行 / runs locally
    │  中文文字 / Chinese text
    ▼
Doubao LLM API (火山方舟 / Volcengine Ark)
    │  宵宫人格回复 / Yoimiya-persona reply
    ▼
Volcengine TTS API
    │  语音 / audio
    ▼
扬声器 / Speaker
```

所有 AI 推理（STT）在本地 GPU 完成，不依赖外部算力。LLM 和 TTS 调用国内 API，无需代理。

STT runs fully local on your GPU. LLM and TTS use domestic Chinese APIs — no VPN needed.

---

## 环境要求 · Requirements

- Python 3.10+
- NVIDIA GPU（显存 ≥ 6GB，用于 Whisper 推理）
- CUDA 12.x 或 13.x（需建立 `cublas64_12.dll` 符号链接，见下方说明）
- 火山引擎账号（豆包 LLM + 豆包语音，均有免费额度）

---

## 快速开始 · Quick Start

### 1. 克隆仓库 · Clone

```bash
git clone https://github.com/serein-nyx/yoimiya-ai.git
cd yoimiya-ai
```

### 2. 安装依赖 · Install dependencies

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 配置环境变量 · Configure environment

复制 `.env.example` 为 `.env`，填入你自己的 key：

Copy `.env.example` to `.env` and fill in your own keys:

```bash
cp .env.example .env
```

```ini
# 火山方舟 LLM · Volcengine Ark LLM
LLM_BACKEND=doubao
ARK_API_KEY=your-ark-api-key
LLM_ENDPOINT_ID=ep-xxxxxxxx-xxxxx

# 豆包语音 TTS · Volcengine TTS
TTS_BACKEND=volc
VOLC_APP_ID=your-app-id
VOLC_ACCESS_TOKEN=your-access-token

# Whisper STT（本地，无需 key）
WHISPER_MODEL=medium
WHISPER_DEVICE=cuda
```

API key 获取方式：

- **ARK_API_KEY + LLM_ENDPOINT_ID**：[火山方舟控制台](https://console.volcengine.com/ark) → 在线推理 → 创建接入点（选 Doubao-Seed-1.6）
- **VOLC_APP_ID + VOLC_ACCESS_TOKEN**：[豆包语音控制台](https://console.volcengine.com/speech/app) → 创建应用 → 勾选"语音合成"

### 4. CUDA 13.x 用户额外步骤 · Extra step for CUDA 13.x users

`ctranslate2` 依赖 `cublas64_12.dll`，CUDA 13 只有 `cublas64_13.dll`。用管理员 PowerShell 建一个符号链接：

`ctranslate2` looks for `cublas64_12.dll`, but CUDA 13 only ships `cublas64_13.dll`. Create a symlink with admin PowerShell:

```powershell
# 先找到实际路径 / Find actual path first
where.exe cublas64_13.dll

# 建符号链接 / Create symlink (adjust path accordingly)
cmd /c mklink "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1\bin\x64\cublas64_12.dll" `
              "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1\bin\x64\cublas64_13.dll"
```

CUDA 12.x 用户无需此步骤。/ CUDA 12.x users can skip this.

### 5. 启动 · Run

```bash
python -m src.main
```

按回车开始说话，再按回车停止，等宵宫回应。输入 `q` 回车退出。

Press Enter to start speaking, Enter again to stop, wait for Yoimiya to respond. Type `q` + Enter to quit.

---

## 项目结构 · Project Structure

```
yoimiya-ai/
├── src/
│   ├── main.py          # 主循环 · Main loop
│   ├── audio.py         # 录音 + 播放 · Recording & playback
│   ├── stt.py           # Whisper 语音识别 · Speech-to-text
│   ├── llm.py           # LLM 抽象层 · LLM abstraction
│   ├── llm_doubao.py    # 豆包实现 + 宵宫人格 · Doubao impl + Yoimiya persona
│   ├── tts.py           # TTS 抽象层 · TTS abstraction
│   ├── tts_volc.py      # 火山引擎 TTS 实现 · Volcengine TTS impl
│   └── config.py        # 配置加载 · Config loader
├── tests/
│   └── test_pipeline.py # 逐模块测试 · Per-module smoke tests
├── .env.example
├── requirements.txt
└── README.md
```

---

## 路线图 · Roadmap

- [x] Phase 1：本地 STT + 云端 LLM + 云端 TTS，完整 pipeline 跑通
- [ ] Phase 2：GPT-SoVITS 训练宵宫音色，替换 TTS 模块
- [ ] Phase 2：Ollama + Qwen2.5-7B 本地 LLM，实现完全离线运行
- [ ] Phase 3：移植到边缘设备（Jetson / 迷你 PC），做成实体盒子

---

## 声明 · Disclaimer

本项目为个人学习项目，非商业用途。

角色版权归米哈游所有。声音版权归配音演员所有。本项目不包含任何游戏资产或声音数据，TTS 音色为通用合成音色。

This is a personal learning project, non-commercial use only.

Character rights belong to miHoYo. Voice rights belong to the respective voice actors. This project contains no game assets or voice data. The TTS voice used is a generic synthesized voice.

---

## License

MIT
