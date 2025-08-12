from typing import Literal, Any
import os
from enum import Enum
import time
import hashlib

from pydantic import BaseModel, Field


TTSEncoding = Literal[
    "pcm_s16le",
    # Not yet supported
    # "pcm_f32le",
    # "pcm_mulaw",
    # "pcm_alaw",
]

TTSModels = Literal["aliyun", "chattts", "openai"]

ModelToModelType = {
    "aliyun": 1,
    "openai": 2,
    "chattts": 3,
}

ModelToSampleRate = {
    "aliyun": 16000,
    "chattts": 24000,
}


class AliyunVoices(str, Enum):
    abin = "abin"
    zhixiaobai = "zhixiaobai"
    zhixiaomei = "zhixiaomei"
    zhixiaoyun = "zhixiaoyun"
    aishuo = "aishuo"
    zhiya = "zhiya"
    ruoxi = "ruoxi"
    xiaoyun = "xiaoyun"
    xiaogang = "xiaogang"
    aixiang = "aixiang"
    aifan = "aifan"


class TTSOptions(BaseModel):
    base_url: str = "https://lbggateway.58corp.com"
    audio_format: Literal["pcm", "wav", "mp3"] = "pcm"
    api_key: str | None = None
    encoding: TTSEncoding = "pcm_s16le"
    sample_rate: int = 16000

    def get_ws_url(self) -> str:
        raise NotImplementedError

    def get_http_url(self) -> str:
        return self.base_url + "/tts"

    def get_query_params():
        raise NotImplementedError


class AliyunTTSOptions(TTSOptions):
    voice: str = "aishuo"
    speed: float = Field(default=5.0, ge=0.0, le=10.0)

    @property
    def model_name(self) -> str:
        return "aliyun"

    @property
    def model_type(self) -> int:
        return ModelToModelType[self.model_name]

    def get_query_params(
        self,
        text: str,
    ) -> dict[str, Any]:
        if self.api_key is None:
            self.api_key = os.getenv("WUBA_TTS_API_KEY")
            if self.api_key is None:
                raise ValueError("WUBA_TTS_API_KEY not found")
        queryParam = {}
        timestamp = round(time.time() * 1000)
        tokenParam = str(timestamp) + self.api_key
        queryParam["timestamp"] = timestamp
        queryParam["token"] = hashlib.md5(tokenParam.encode("utf8")).hexdigest()
        queryParam["text"] = text
        queryParam["modelType"] = self.model_type
        queryParam["extend"] = {"format": self.audio_format, "voice": self.voice}
        speech_rate = ((self.speed - 5) / 5) * 500
        queryParam["extend"]["speech_rate"] = int(speech_rate)
        return queryParam


class ChatTTSVoices(str, Enum):
    female = "female"
    male = "male"


class ChatTTSOptions(TTSOptions):
    voice: ChatTTSVoices = ChatTTSVoices.female
    speed: float = Field(default=5.0, ge=0.0, le=10.0)
    sample_rate: int = 24000

    @property
    def model_name(self) -> str:
        return "chattts"

    @property
    def model_type(self) -> int:
        return ModelToModelType[self.model_name]

    def get_query_params(
        self,
        text: str,
    ) -> dict[str, Any]:
        if self.api_key is None:
            self.api_key = os.getenv("WUBA_TTS_API_KEY")
            if self.api_key is None:
                raise ValueError("WUBA_TTS_API_KEY not found")
        queryParam = {}
        timestamp = round(time.time() * 1000)
        tokenParam = str(timestamp) + self.api_key
        queryParam["timestamp"] = timestamp
        queryParam["token"] = hashlib.md5(tokenParam.encode("utf8")).hexdigest()
        queryParam["text"] = text
        queryParam["modelType"] = self.model_type
        queryParam["extend"] = {"format": self.audio_format, "voice": self.voice.value}
        speech_rate = ((self.speed - 5) / 5) * 500
        queryParam["extend"]["speech_rate"] = int(speech_rate)
        return queryParam
