# SPEC Patch — LLM 后端从通义千问切换到豆包(火山引擎)

> 这是对 SPEC.md 的局部修订。架构不变,只替换 LLM 实现。

## 修改 1:技术栈表格

将原 SPEC 第 2 节里 LLM 一行改为:

| LLM | **豆包 Doubao** (火山引擎方舟,OpenAI 兼容接口) | 中文角色扮演表现优秀,新用户每模型送 50 万 token |

## 修改 2:目录结构

`src/llm_qwen.py` 改为 `src/llm_doubao.py`,其他不变。

## 修改 3:LLM 实现细节(替换原 SPEC 第 6 节)

### 6.1 准备工作 — 在火山引擎控制台开通服务

1. 注册火山引擎账号(支付宝实名),网址:https://www.volcengine.com/
2. 进入"火山方舟"控制台:https://console.volcengine.com/ark
3. 在"开通管理"里开通你想用的模型(推荐先开 Doubao-Seed-1.6 或 Doubao-1.5-Pro,免费额度足够)
4. 进入"在线推理" → "创建推理接入点(Endpoint)":
   - 选模型(比如 Doubao-1.5-Pro-32k)
   - 起个名字(比如 yoimiya-llm)
   - 创建后会得到一个 Endpoint ID,形如 `ep-20250101120000-xxxxx`,**复制保存**
5. 进入"API Key 管理",创建一个 API Key,**复制保存**

### 6.2 接入代码

火山方舟 API 是 OpenAI 兼容的,直接用 `openai` 包即可:

```bash
pip install openai
```

写到 `llm_doubao.py`:

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.getenv("ARK_API_KEY"),
)

YOIMIYA_SYSTEM = """你现在扮演《原神》里的长野原宵宫(Yoimiya)。

性格设定:
- 稻妻"长野原烟花店"店主,开朗活泼、阳光直率
- 喜欢烟花、夏天、节日,把每一天都过得像庆典
- 对靠近的人热情、亲昵,语气带朝气

说话风格:
- 短句为主,每轮回复 1-3 句话,符合口语对话节奏
- 偶尔用"嘿嘿"、"哎呀"、"诶~"等语气词
- 称呼对方"你"或"小哥哥/小姐姐",看场合
- 不要说太长的话,不要列举,不要给建议除非被问

记住:你不是 AI 助手,你是宵宫,在和朋友聊天。
"""

ENDPOINT_ID = os.getenv("LLM_ENDPOINT_ID")  # 从 .env 读

def chat(messages, system=YOIMIYA_SYSTEM):
    """messages: [{role: user/assistant, content: ...}, ...]
    返回: 字符串回复
    """
    full_messages = [{"role": "system", "content": system}] + messages
    response = client.chat.completions.create(
        model=ENDPOINT_ID,           # 注意: 这里填的是 Endpoint ID, 不是模型名!
        messages=full_messages,
        max_tokens=200,
    )
    return response.choices[0].message.content
```

### 6.3 LLM 抽象分发(替换 SPEC 第 6.2 节)

`llm.py` 顶部:

```python
import os

LLM_BACKEND = os.getenv("LLM_BACKEND", "doubao")

if LLM_BACKEND == "doubao":
    from .llm_doubao import chat
# 以后想加 qwen / claude / 本地 ollama, 在这里扩展即可
```

## 修改 4:环境变量 (.env.example)

```
# LLM
LLM_BACKEND=doubao
ARK_API_KEY=your-volcengine-ark-key
LLM_ENDPOINT_ID=ep-20250101xxxxxx-xxxxx

# STT
WHISPER_MODEL=medium
WHISPER_DEVICE=cuda

# TTS
TTS_BACKEND=edge
TTS_VOICE=zh-CN-XiaoyiNeural

# 录音
SAMPLE_RATE=16000
RECORD_SECONDS=5
```

## 修改 5:实施顺序里的 Step 4

原:实现 `llm.py` + `llm_qwen.py`(包含宵宫人格),测试:输入"你好"能拿到符合人设的回复

改为:实现 `llm.py` + `llm_doubao.py`(包含宵宫人格),测试:输入"你好"能拿到符合人设的回复。**测试前先确认 .env 里的 ARK_API_KEY 和 LLM_ENDPOINT_ID 都填对了**。

## 常见坑

1. **Endpoint ID 和模型名混淆**:模型名是 `doubao-1.5-pro-32k`,但你 API 调用要用 `ep-xxxxx`。新手最常犯这个错,会报 "model not found"。
2. **base_url 别写错**:必须是 `https://ark.cn-beijing.volces.com/api/v3`,不要漏 `/api/v3`。
3. **免费额度有有效期**:50 万 token 通常 6 个月内用完。够你这个项目玩很久了,但不是永久。
4. **每个模型分别开通**:你想用哪个就要单独开通,有的模型默认不开。
