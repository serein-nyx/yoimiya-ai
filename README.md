# Yoimiya AI

本地语音对话程序，用麦克风说话，程序以《原神》角色**长野原宵宫**的人格用语音回复。

## 技术栈

| 模块 | 选型 |
|---|---|
| 录音 / 播放 | sounddevice + pygame |
| 语音识别 (STT) | faster-whisper (medium, CUDA) |
| 大模型 (LLM) | 豆包 Doubao，火山方舟 OpenAI 兼容接口 |
| 语音合成 (TTS) | edge-tts（Phase 1 占位） |

## 环境要求

- Python 3.10+
- NVIDIA 显卡 + CUDA 12.x（用于 faster-whisper GPU 推理）
- 麦克风 + 扬声器

## 快速开始

```bash
# 1. 克隆 & 进入目录
git clone <repo-url>
cd yoimiya-ai

# 2. 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
copy .env.example .env
# 编辑 .env，填入 ARK_API_KEY 和 LLM_ENDPOINT_ID

# 5. 运行
python -m src.main
```

## 对话操作

- 按 **回车** 开始录音（默认 5 秒）
- 录音结束后自动识别 → LLM 回复 → 语音播放
- 输入 **q** 退出

## Phase 路线图

- **Phase 1**（当前）：edge-tts 占位音色，跑通完整 pipeline
- **Phase 2**：接入 GPT-SoVITS 本地推理，实现真正的宵宫音色
- **Phase 3**（可选）：移植到树莓派等硬件
