import os
from dotenv import load_dotenv

load_dotenv()

SAMPLE_RATE     = int(os.getenv("SAMPLE_RATE", "16000"))
RECORD_SECONDS  = int(os.getenv("RECORD_SECONDS", "5"))
WHISPER_MODEL   = os.getenv("WHISPER_MODEL", "medium")
WHISPER_DEVICE  = os.getenv("WHISPER_DEVICE", "cuda")
HF_HOME         = os.getenv("HF_HOME", r"D:\AI\models\huggingface")
WHISPER_CACHE   = os.path.join(HF_HOME, "hub")
HF_ENDPOINT     = os.getenv("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
TTS_BACKEND        = os.getenv("TTS_BACKEND", "edge")
TTS_VOICE          = os.getenv("TTS_VOICE", "zh-CN-XiaoyiNeural")
VOLC_APP_ID        = os.getenv("VOLC_APP_ID", "")
VOLC_ACCESS_TOKEN  = os.getenv("VOLC_ACCESS_TOKEN", "")
LLM_BACKEND        = os.getenv("LLM_BACKEND", "doubao")
ARK_API_KEY     = os.getenv("ARK_API_KEY", "")
LLM_ENDPOINT_ID = os.getenv("LLM_ENDPOINT_ID", "")
