import os

from . import audio, config, llm, stt, tts

_MAX_TURNS = 20  # 保留最近 N 轮对话（每轮 = user + assistant 共 2 条消息）


def run() -> None:
    print("=" * 48)
    print("  宵宫 AI 语音助手")
    print("  按回车开始说话，输入 q 回车退出")
    print("=" * 48)

    messages: list[dict] = []

    while True:
        try:
            cmd = input("\n按回车开始说话，q 退出 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if cmd.lower() == "q":
            print("再见！")
            break

        # ── 录音 ──────────────────────────────────────────
        audio_data = audio.record_until_enter()

        # ── STT ───────────────────────────────────────────
        print("[STT] 识别中...", end="", flush=True)
        text = stt.transcribe(audio_data, config.SAMPLE_RATE)
        if not text:
            print("\r[提示] 没有识别到内容，请重新说话")
            continue
        print(f"\r[你] {text}          ")

        # ── LLM ───────────────────────────────────────────
        messages.append({"role": "user", "content": text})
        print("[宵宫] 思考中...", end="", flush=True)
        try:
            reply = llm.chat(messages)
        except Exception as e:
            print(f"\r[错误] LLM 调用失败: {e}")
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": reply})

        # 保留最近 _MAX_TURNS 轮
        if len(messages) > _MAX_TURNS * 2:
            messages = messages[-_MAX_TURNS * 2:]

        print(f"\r[宵宫] {reply}          ")

        # ── TTS + 播放 ────────────────────────────────────
        try:
            path = tts.synthesize(reply)
            audio.play(path)
            os.unlink(path)
        except Exception as e:
            print(f"[TTS 错误] {e}")


if __name__ == "__main__":
    run()
