from . import config

if config.TTS_BACKEND == "edge":
    from .tts_edge import synthesize  # noqa: F401
elif config.TTS_BACKEND == "volc":
    from .tts_volc import synthesize  # noqa: F401
else:
    raise ValueError(f"[TTS] 未知后端: {config.TTS_BACKEND}，目前仅支持 edge | volc | sovits")
