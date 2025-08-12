from __future__ import annotations

import asyncio
import weakref
from typing_extensions import Self
import time

import aiohttp

from livekit.agents import (
    APIConnectOptions,
    tts,
    utils,
)
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS
from osc_data.text_stream import TextStreamSentencizer

from .log import logger
from .models import (
    TTSOptions,
    AliyunTTSOptions,
    ChatTTSVoices,
    ChatTTSOptions,
)


class TTS(tts.TTS):
    def __init__(
        self,
        *,
        http_session: aiohttp.ClientSession | None = None,
        options: TTSOptions | None = None,
    ) -> None:
        """
        Create a new instance of 58 LBG TTS service.

        Args:
            api_key (str, optional): The Wuba API key. If not provided, it will be read from the WUBA_TTS_API_KEY environment variable.
            http_session (aiohttp.ClientSession | None, optional): An existing aiohttp ClientSession to use. If not provided, a new session will be created.
            max_session_duration (int, optional): The maximum duration (in seconds) for a single session. Defaults to 600.
            stream (bool, optional): Whether to stream the audio. Defaults to True.
        """  # noqa: E501

        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=True),
            sample_rate=16000,
            num_channels=1,
        )
        self._session = http_session
        self._streams = weakref.WeakSet[SynthesizeStream]()
        self._opts: TTSOptions = options

    def with_aliyun(
        self,
        voice: str,
        speed: float = 5.0,
        api_key: str | None = None,
    ) -> Self:
        """
        Configure the TTS service with Aliyun TTS options.

        Args:
            voice (AliyunVoices): the voice to use for the TTS service.
            speed (float): the speed of the voice. Must be between 0.0 and 10.0. The default is 5.0.
            api_key (str | None, optional): the API key to use for the TTS service. If not provided, it will be read from the WUBA_TTS_API_KEY environment variable. Defaults to None.
        """
        self._opts = AliyunTTSOptions(voice=voice, speed=speed, api_key=api_key)
        return self

    def with_chattts(
        self, voice: ChatTTSVoices, speed: float = 5.0, api_key: str | None = None
    ):
        """
        Configure the TTS service with ChatTTS options.
        Args:
            voice (ChatTTSVoices): the voice to use for the TTS service.
            speed (float): the speed of the voice. Must be between 0.0 and 10.0. The default is 5.0.
            api_key (str | None, optional): the API key to use for the TTS service. If not provided, it will be read from the WUBA_TTS_API_KEY environment variable. Defaults to None.
        """
        self._opts = ChatTTSOptions(voice=voice, speed=speed, api_key=api_key)
        return self

    async def _connect_ws(self, timeout: float) -> aiohttp.ClientWebSocketResponse:
        session = self._ensure_session()
        url = self._opts.get_ws_url()
        return await asyncio.wait_for(session.ws_connect(url), timeout=timeout)

    async def _close_ws(self, ws: aiohttp.ClientWebSocketResponse):
        await ws.close()

    def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = utils.http_context.http_session()

        return self._session

    def synthesize(
        self,
        text: str,
        *,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ):
        raise NotImplementedError

    def stream(
        self, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS
    ) -> SynthesizeStream:
        return SynthesizeStream(
            tts=self,
            opts=self._opts,
            session=self._ensure_session(),
            conn_options=conn_options,
        )

    async def aclose(self) -> None:
        for stream in list(self._streams):
            await stream.aclose()
        self._streams.clear()
        await super().aclose()


class SynthesizeStream(tts.SynthesizeStream):
    def __init__(
        self,
        *,
        tts: TTS,
        opts: TTSOptions,
        session: aiohttp.ClientSession,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ):
        super().__init__(tts=tts, conn_options=conn_options)
        self._opts, self._session = opts, session

    async def _run(self, emitter: tts.AudioEmitter) -> None:
        request_id = utils.shortuuid()
        emitter.initialize(
            request_id=request_id,
            sample_rate=self._opts.sample_rate,
            mime_type="audio/pcm",
            frame_size_ms=200,
            stream=True,
            num_channels=1,
        )
        sentencizer = TextStreamSentencizer(
            min_sentence_length=10, use_level2_threshold=50, use_level3_threshold=100
        )
        first_sentence_spend = None
        start_time = time.perf_counter()
        async for token in self._input_ch:
            if isinstance(token, self._FlushSentinel):
                sentences = sentencizer.flush()
            else:
                sentences = sentencizer.push(text=token)
            for sentence in sentences:
                if first_sentence_spend is None:
                    first_sentence_spend = time.perf_counter() - start_time
                    logger.info(
                        "llm first sentence", extra={"spent": str(first_sentence_spend)}
                    )
                if len(sentence.strip()) > 0:
                    emitter.start_segment(segment_id=utils.shortuuid())
                    first_response_spend = None
                    logger.info("tts start", extra={"sentence": sentence})
                    data = self._opts.get_query_params(text=sentence)
                    if first_response_spend is None:
                        start_time = time.perf_counter()
                    async with self._session.post(
                        self._opts.get_http_url(),
                        json=data,
                        timeout=aiohttp.ClientTimeout(
                            total=30,
                            sock_connect=self._conn_options.timeout,
                        ),
                    ) as resp:
                        resp.raise_for_status()
                        async for data, _ in resp.content.iter_chunks():
                            if first_response_spend is None:
                                first_response_spend = time.perf_counter() - start_time
                                logger.info(
                                    "tts first response",
                                    extra={"spent": str(first_response_spend)},
                                )
                            emitter.push(data=data)
                    self._pushed_text = self._pushed_text.replace(sentence, "")
                    emitter.end_segment()
                    logger.info("tts end")
