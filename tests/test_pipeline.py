"""
Smoke tests — run each step independently:
  Step 2:  python tests/test_pipeline.py record
  Step 3:  python tests/test_pipeline.py stt
  Step 4:  python tests/test_pipeline.py llm
  Step 5:  python tests/test_pipeline.py tts
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import audio, config


def test_record_playback():
    print("=== Step 2: 录音回放测试 ===")
    print(f"采样率: {config.SAMPLE_RATE} Hz  时长: {config.RECORD_SECONDS}s")

    data = audio.record()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name

    audio.save_wav(data, config.SAMPLE_RATE, wav_path)
    print(f"[保存] {wav_path}  ({os.path.getsize(wav_path)} bytes)")

    print("[回放] 播放中...")
    audio.play(wav_path)

    os.unlink(wav_path)
    print("[完成] Step 2 通过 OK")


def test_stt():
    from src import stt

    print("=== Step 3: 语音识别测试 ===")
    print(f"模型: {config.WHISPER_MODEL}  设备: {config.WHISPER_DEVICE}")

    data = audio.record()

    print("[STT] 识别中...")
    text = stt.transcribe(data, config.SAMPLE_RATE)

    if text:
        print(f"[STT] 识别结果: {text}")
    else:
        print("[STT] 未识别到内容 (说话声音太小或静音?)")

    print("[完成] Step 3 通过 OK")


def test_llm():
    from src import llm

    print("=== Step 4: LLM 对话测试 ===")
    print(f"后端: {config.LLM_BACKEND}  Endpoint: {config.LLM_ENDPOINT_ID}")

    messages = [{"role": "user", "content": "你好"}]
    print("[LLM] 发送: 你好")
    reply = llm.chat(messages)
    print(f"[LLM] 回复: {reply}")

    print("[完成] Step 4 通过 OK")


def test_tts():
    from src import tts

    print("=== Step 5: TTS 语音合成测试 ===")
    print(f"后端: {config.TTS_BACKEND}  音色: {config.TTS_VOICE}")

    text = "你来啦你来啦！今天怎么有空过来？"
    print(f"[TTS] 合成: {text}")
    path = tts.synthesize(text)
    print(f"[TTS] 音频文件: {path}")

    print("[TTS] 播放中...")
    audio.play(path)

    os.unlink(path)
    print("[完成] Step 5 通过 OK")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "record"
    if cmd == "record":
        test_record_playback()
    elif cmd == "stt":
        test_stt()
    elif cmd == "llm":
        test_llm()
    elif cmd == "tts":
        test_tts()
    else:
        print(f"未知命令: {cmd}  可选: record | stt | llm | tts")
        sys.exit(1)
