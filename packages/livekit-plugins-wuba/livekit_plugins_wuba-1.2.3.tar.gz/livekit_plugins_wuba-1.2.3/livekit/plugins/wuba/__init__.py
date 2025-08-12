from .tts import TTS
from .stt import STT
from .dify import Dify
from .silero import VAD
from .turn_detector import MultilingualTurnDetector
from .models import AliyunVoices, ChatTTSVoices
from .version import __version__

__all__ = [
    "TTS",
    "AliyunVoices",
    "ChatTTSVoices",
    "Dify",
    "STT",
    "VAD",
    "MultilingualTurnDetector",
    "__version__",
]

from livekit.agents import Plugin

from .log import logger


class WubaPlugin(Plugin):
    def __init__(self):
        super().__init__(__name__, __version__, __package__, logger)

    def download_files(self) -> None:
        from transformers import AutoTokenizer  # type: ignore

        from .turn_detector import (
            _download_from_hf_hub,
            HG_MODEL,
            MODEL_REVISION,
            ONNX_FILENAME,
        )

        AutoTokenizer.from_pretrained(HG_MODEL, revision=MODEL_REVISION)
        _download_from_hf_hub(
            HG_MODEL, ONNX_FILENAME, subfolder="onnx", revision=MODEL_REVISION
        )
        _download_from_hf_hub(HG_MODEL, "languages.json", revision=MODEL_REVISION)


Plugin.register_plugin(WubaPlugin())

# Cleanup docs of unexported modules
_module = dir()
NOT_IN_ALL = [m for m in _module if m not in __all__]

__pdoc__ = {}

for n in NOT_IN_ALL:
    __pdoc__[n] = False
