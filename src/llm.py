from . import config

if config.LLM_BACKEND == "doubao":
    from .llm_doubao import chat  # noqa: F401
else:
    raise ValueError(f"[LLM] 未知后端: {config.LLM_BACKEND}，目前仅支持 doubao")
