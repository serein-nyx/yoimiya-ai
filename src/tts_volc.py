import base64
import tempfile
import uuid

import httpx

from . import config

_API_URL = "https://openspeech.bytedance.com/api/v1/tts"


def synthesize(text: str) -> str:
    """合成文本为语音，返回临时 .mp3 文件路径（调用方负责删除）。"""
    if not config.VOLC_APP_ID:
        raise ValueError("[TTS] VOLC_APP_ID 未配置，请在 .env 中填写")
    if not config.VOLC_ACCESS_TOKEN:
        raise ValueError("[TTS] VOLC_ACCESS_TOKEN 未配置，请在 .env 中填写")

    payload = {
        "app": {
            "appid": config.VOLC_APP_ID,
            "token": config.VOLC_ACCESS_TOKEN,
            "cluster": "volcano_tts",
        },
        "user": {"uid": "yoimiya-ai"},
        "audio": {
            "voice_type": config.TTS_VOICE,
            "encoding": "mp3",
            "speed_ratio": 1.0,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "text_type": "plain",
            "operation": "query",
        },
    }
    headers = {"Authorization": f"Bearer;{config.VOLC_ACCESS_TOKEN}"}
    resp = httpx.post(_API_URL, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    body = resp.json()
    if body.get("code") != 3000:
        raise RuntimeError(
            f"[TTS] 火山 TTS 错误 code={body.get('code')} msg={body.get('message')}"
        )

    audio_bytes = base64.b64decode(body["data"])
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(audio_bytes)
        return f.name
