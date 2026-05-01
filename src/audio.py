import threading
import time
import wave

import numpy as np
import pygame
import sounddevice as sd

from . import config


def record(duration: int = None, sample_rate: int = None) -> np.ndarray:
    duration    = duration    or config.RECORD_SECONDS
    sample_rate = sample_rate or config.SAMPLE_RATE

    print(f"[录音] 开始，请说话...", flush=True)
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
    )
    for remaining in range(duration, 0, -1):
        print(f"\r[录音] 剩余 {remaining}s ...", end="", flush=True)
        time.sleep(1)
    sd.wait()
    print("\r[录音] 完成            ")

    peak = float(np.abs(audio_data).max())
    print(f"[录音] 峰值电平: {peak:.3f}")
    return audio_data.squeeze()


def save_wav(audio: np.ndarray, sample_rate: int, path: str) -> str:
    audio_clipped = np.clip(audio, -1.0, 1.0)
    audio_int16   = (audio_clipped * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
    return path


def _ensure_mixer() -> None:
    if not pygame.mixer.get_init():
        pygame.mixer.init()


def record_until_enter(max_seconds: int = 60, sample_rate: int = None) -> np.ndarray:
    """开始录音，用户按回车停止，最长录 max_seconds 秒。"""
    sample_rate = sample_rate or config.SAMPLE_RATE
    print(f"[录音] 录音中... 按回车停止（最长 {max_seconds}s）", flush=True)

    chunks = []
    stop_event = threading.Event()

    def _wait_enter():
        input()
        stop_event.set()

    def _callback(indata, frames, time_info, status):
        chunks.append(indata.copy())

    t = threading.Thread(target=_wait_enter, daemon=True)
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype="float32", callback=_callback):
        t.start()
        stop_event.wait(timeout=max_seconds)

    if not chunks:
        return np.zeros(0, dtype="float32")

    audio = np.concatenate(chunks).squeeze()
    peak = float(np.abs(audio).max())
    print(f"[录音] 峰值电平: {peak:.3f}")
    return audio


def play(path: str) -> None:
    _ensure_mixer()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)
    pygame.mixer.music.unload()  # 释放文件句柄，允许外部删除临时文件
