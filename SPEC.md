# Yoimiya AI Chat — 项目规范

> 这份文档是项目的 single source of truth。Claude Code 应当先读完这份文档,再按下方的实施顺序逐步搭建。

## 1. 项目目标

在 PC 上构建一个语音对话程序,用户用麦克风说话,程序以"长野原宵宫"(《原神》角色)的人格用语音回复。

**Phase 1(本SPEC的范围)**:跑通完整pipeline,使用占位TTS声音。
**Phase 2(后续)**:把TTS换成GPT-SoVITS本地推理,实现真正的宵宫音色。
**Phase 3(可选,长期)**:移植到树莓派等硬件设备。

## 2. 技术栈(已决定,不要再讨论替代方案)

| 模块 | 选型 | 理由 |
|---|---|---|
| 语言 | Python 3.10+ | 主流AI生态 |
| 录音/播放 | sounddevice + pygame | 跨平台,API简单 |
| 语音识别(STT) | faster-whisper (base模型) | 本地运行,中文效果好 |
| 大模型(LLM) | Anthropic Claude API (claude-sonnet-4-6) | 角色扮演稳定 |
| 语音合成(TTS) | edge-tts (zh-CN-XiaoyiNeural) | 占位用,Phase 2替换 |
| 配置管理 | python-dotenv | API key隔离 |

## 3. 目录结构

```
yoimiya-ai/
├── README.md
├── SPEC.md                     # 本文件
├── requirements.txt
├── .env.example                # 提交到git
├── .env                        # 不提交,加到.gitignore
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── main.py                 # CLI入口 + 主循环
│   ├── audio.py                # 录音 + 播放
│   ├── stt.py                  # Whisper封装
│   ├── llm.py                  # Claude封装 + 宵宫人格
│   ├── tts.py                  # TTS抽象层(关键: 必须可替换)
│   └── config.py               # 配置加载
└── tests/
    └── test_pipeline.py        # 各模块的smoke test
```

## 4. 关键设计原则

**TTS必须是抽象接口**。`tts.py` 应定义一个 `synthesize(text: str) -> str` 函数(返回音频文件路径),`main.py` 只调用这个接口。Phase 2 替换 TTS 实现时,`main.py` 一行不用改。

**所有模块解耦**。`audio.py` / `stt.py` / `llm.py` / `tts.py` 之间不互相 import,只通过 `main.py` 串联。每个模块都能被独立测试。

**配置不写死**。模型名、采样率、录音时长、TTS音色等参数都放 `config.py`,从 `.env` 或常量读取。

## 5. 宵宫人格 Prompt(写在 `llm.py` 里)

```
你现在扮演《原神》里的长野原宵宫(Yoimiya)。

性格设定:
- 稻妻"长野原烟花店"店主,开朗活泼、阳光直率
- 喜欢烟花、夏天、节日,把每一天都过得像庆典
- 对靠近的人热情、亲昵,语气带朝气

说话风格:
- 短句为主,每轮回复1-3句话,符合口语对话节奏
- 偶尔用"嘿嘿"、"哎呀"、"诶~"等语气词
- 称呼对方"你"或"小哥哥/小姐姐",看场合
- 不要说太长的话,不要列举,不要给建议除非被问

记住:你不是AI助手,你是宵宫,在和朋友聊天。
```

## 6. 实施顺序(Claude Code 按这个顺序写)

**Step 1**:创建项目骨架(目录、`requirements.txt`、`.gitignore`、`.env.example`、`README.md`)

**Step 2**:实现 `config.py` 和 `audio.py`,写一个独立测试:能录5秒音频并立刻回放。

**Step 3**:实现 `stt.py`,测试:对Step 2录的音频能输出中文文本。

**Step 4**:实现 `llm.py`(包含宵宫人格),测试:输入"你好"能拿到符合人设的回复。

**Step 5**:实现 `tts.py`(Edge TTS版本),测试:给定一段文字能合成并播放。

**Step 6**:在 `main.py` 里串联所有模块,写CLI主循环:回车录音 → STT → LLM(带历史) → TTS → 播放,`q` 退出。

**Step 7**:对话历史管理(在 `main.py` 里维护一个 `messages` 列表传给Claude,实现多轮对话)。

每一步完成后必须能独立运行测试通过,再进入下一步。**不要一次性把所有代码写完**。

## 7. 验收标准(Phase 1 完成的定义)

- [ ] `pip install -r requirements.txt` 一次到位,无手工补包
- [ ] `python -m src.main` 能启动
- [ ] 按回车后能录到音频(看到电平变化或时长提示)
- [ ] 中文识别准确率主观可接受(短句基本不出错)
- [ ] 宵宫的回复符合人设(语气活泼、短句、不像AI助手)
- [ ] 能持续多轮对话,宵宫记得上下文
- [ ] 输入 q 能干净退出

## 8. Phase 2 需要预留的扩展点(写代码时就要考虑)

- `tts.py` 的 `synthesize()` 接口要稳定。Phase 2 时新建一个 `tts_sovits.py` 实现同样接口,`main.py` 通过配置切换实现。
- 配置项里预留 `TTS_BACKEND = "edge" | "sovits"`,`config.py` 据此选择 import 哪个实现。
- 不要在 `main.py` 里写死 `import edge_tts`。

## 9. 环境变量 (.env.example)

```
ANTHROPIC_API_KEY=sk-ant-xxxxx
WHISPER_MODEL=large-v3 
TTS_BACKEND=edge
LLM_MODEL=claude-sonnet-4-6
```
