import os

import numpy as np
from faster_whisper import WhisperModel

from . import config

_model: WhisperModel = None
_active_device: str = None  # tracks the device actually in use (may differ from config after fallback)


def _is_cuda_lib_error(e: Exception) -> bool:
    msg = str(e).lower()
    return any(k in msg for k in ("cublas", "cudnn", "cuda", "dll", "library"))


def _load_model(device: str) -> WhisperModel:
    compute_type = "float16" if device == "cuda" else "int8"
    print(f"[STT] 加载模型 {config.WHISPER_MODEL} @ {device} ({compute_type})")
    print(f"[STT] 首次运行会从 {config.HF_ENDPOINT} 下载模型，请耐心等待...")
    return WhisperModel(
        config.WHISPER_MODEL,
        device=device,
        compute_type=compute_type,
        download_root=config.WHISPER_CACHE,
    )


def _get_model() -> WhisperModel:
    global _model, _active_device
    if _model is None:
        os.environ["HF_ENDPOINT"] = config.HF_ENDPOINT
        device = config.WHISPER_DEVICE
        try:
            _model = _load_model(device)
            _active_device = device
        except RuntimeError as e:
            if device == "cuda" and _is_cuda_lib_error(e):
                print(f"[STT] CUDA 初始化失败 ({e})，降级到 CPU int8")
                _model = _load_model("cpu")
                _active_device = "cpu"
            else:
                raise
        print("[STT] 模型加载完成")
    return _model


def transcribe(audio: np.ndarray, sample_rate: int = None) -> str:
    """将 float32 numpy 音频数组转为中文文本。"""
    global _model, _active_device
    sample_rate = sample_rate or config.SAMPLE_RATE
    model = _get_model()
    try:
        segments, _ = model.transcribe(
            audio,
            beam_size=5,
            language="zh",
            vad_filter=True,
        )
        return "".join(seg.text for seg in segments).strip()
    except RuntimeError as e:
        # cublas64_12.dll / cudnn DLL missing at inference time (CUDA 13 + CT2 built for CUDA 12)
        if _active_device == "cuda" and _is_cuda_lib_error(e):
            print(f"[STT] CUDA 推理失败 ({e})，重置模型并降级到 CPU int8")
            _model = None
            _active_device = "cpu"
            return transcribe(audio, sample_rate)
        raise
