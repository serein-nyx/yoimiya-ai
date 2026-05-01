import asyncio
import tempfile

import edge_tts

from . import config


async def _save(text: str, voice: str, path: str) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)


def synthesize(text: str) -> str:
    """合成文本为语音，返回临时 .mp3 文件路径（调用方负责删除）。"""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        path = f.name
    asyncio.run(_save(text, config.TTS_VOICE, path))
    return path
