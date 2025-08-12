from __future__ import annotations

import asyncio
import json
import os
import weakref
from dataclasses import dataclass
from typing import Literal, Generic, Optional, TypeVar, Callable
import time
from urllib.parse import urlencode
import hashlib

import aiohttp

from livekit import rtc
from livekit.agents import (
    DEFAULT_API_CONNECT_OPTIONS,
    APIConnectOptions,
    stt,
    utils,
)
from livekit.agents.types import (
    NOT_GIVEN,
    NotGivenOr,
)
from livekit.agents.utils import AudioBuffer

from .log import logger


@dataclass
class AliyunSTTOptions:
    api_key: str | None = None
    audio_format: Literal["pcm", "wav", "mp3"] = "pcm"
    sample_rate: int = 16000
    base_url: str = "wss://lbggateway.58corp.com"

    def get_ws_url(self):
        queryParam = {}
        timestamp = round(time.time() * 1000)
        if self.api_key is None:
            self.api_key = os.environ.get("WUBA_STT_API_KEY")
        if self.api_key is None:
            raise ValueError("WUBA_STT_API_KEY is not set")
        # 设置key
        tokenParam = str(timestamp) + self.api_key
        queryParam["timestamp"] = timestamp
        queryParam["token"] = hashlib.md5(tokenParam.encode("utf8")).hexdigest()
        queryParam["modelType"] = 1
        queryParam["extend"] = json.dumps({"format": self.audio_format})
        url = f"{self.base_url}/realTimeAsr?" + urlencode(queryParam)
        return url


@dataclass
class ParaformerSTTOptions:
    base_url: str = "wss://lbggateway.58corp.com"
    sample_rate: int = 16000
    model: Literal["paraformer", "sensevoice"] = "paraformer"

    def get_ws_url(self):
        return f"{self.base_url}/asr/realtime?model={self.model}"


class STT(stt.STT):
    def __init__(
        self,
        *,
        opts: AliyunSTTOptions | ParaformerSTTOptions = None,
        http_session: aiohttp.ClientSession | None = None,
        interim_results: bool = True,
    ) -> None:
        super().__init__(
            capabilities=stt.STTCapabilities(
                streaming=True, interim_results=interim_results
            )
        )

        self._opts = opts

        self._session = http_session
        self._streams = weakref.WeakSet[SpeechStream]()

    def with_aliyun(
        self,
        audio_format: Literal["pcm", "wav", "mp3"] = "pcm",
        api_key: str | None = None,
    ) -> STT:
        self._opts = AliyunSTTOptions(
            api_key=api_key,
            audio_format=audio_format,
        )
        return self

    def with_paraformer(
        self,
        base_url: str = "wss://lbggateway.58corp.com",
        sample_rate: int = 16000,
        model: Literal["paraformer", "sensevoice"] = "paraformer",
    ) -> STT:
        self._opts = ParaformerSTTOptions(
            base_url=base_url, sample_rate=sample_rate, model=model
        )
        return self

    def _ensure_session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = utils.http_context.http_session()

        return self._session

    async def _recognize_impl(
        self,
        buffer: AudioBuffer,
        *,
        language: NotGivenOr[str] = NOT_GIVEN,
        conn_options: APIConnectOptions,
    ) -> stt.SpeechEvent:
        raise NotImplementedError("not implemented")  # 非流式识别接口

    def stream(
        self,
        *,
        language: NotGivenOr[str] = NOT_GIVEN,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> SpeechStream:
        stream = SpeechStream(
            stt=self,
            conn_options=conn_options,
            opts=self._opts,
            http_session=self._ensure_session(),
        )
        self._streams.add(stream)
        return stream


class SpeechStream(stt.SpeechStream):
    def __init__(
        self,
        *,
        stt: STT,
        opts: AliyunSTTOptions | ParaformerSTTOptions,
        conn_options: APIConnectOptions,
        http_session: aiohttp.ClientSession,
    ) -> None:
        super().__init__(
            stt=stt, conn_options=conn_options, sample_rate=opts.sample_rate
        )

        self._opts = opts
        self._session = http_session
        self._speaking = False
        self._audio_duration_collector = PeriodicCollector(
            callback=self._on_audio_duration_report,
            duration=5.0,
        )

        self._request_id = utils.shortuuid()
        self._reconnect_event = asyncio.Event()

    async def _run(self) -> None:
        if isinstance(self._opts, AliyunSTTOptions):
            await self._run_aliyun()
        elif isinstance(self._opts, ParaformerSTTOptions):
            await self._run_paraformer()

    async def _run_paraformer(self) -> None:
        closing_ws = False

        @utils.log_exceptions(logger=logger)
        async def send_task(ws: aiohttp.ClientWebSocketResponse):
            nonlocal closing_ws

            samples_50ms = (self._opts.sample_rate // 1000) * 50
            audio_bstream = utils.audio.AudioByteStream(
                sample_rate=self._opts.sample_rate,
                num_channels=1,
                samples_per_channel=samples_50ms,
            )

            has_ended = False
            async for frame in self._input_ch:
                frames: list[rtc.AudioFrame] = []
                if isinstance(frame, rtc.AudioFrame):
                    frames.extend(audio_bstream.write(frame.data.tobytes()))
                elif isinstance(frame, self._FlushSentinel):
                    frames.extend(audio_bstream.flush())
                    has_ended = True

                for frame in frames:
                    self._audio_duration_collector.push(frame.duration)
                    try:
                        # logger.info(f"frame size: {frame.data.shape}")
                        await ws.send_bytes(frame.data.tobytes())
                    except Exception:
                        closing_ws = True

                    if has_ended:
                        self._audio_duration_collector.flush()
                        await ws.send_str("close")
                        has_ended = False
                        closing_ws = True

        @utils.log_exceptions(logger=logger)
        async def recv_task(ws: aiohttp.ClientWebSocketResponse):
            nonlocal closing_ws
            while True:
                msg = await ws.receive()
                if msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSING,
                ):
                    if closing_ws:  # close is expected
                        return

                    # this will trigger a reconnection, see the _run loop
                    logger.error("connection closed unexpectedly")
                    break

                try:
                    self._process_stream_event_paraformer(json.loads(msg.data))
                except Exception:
                    logger.exception("failed to process paraformer message")

        ws: aiohttp.ClientWebSocketResponse | None = None

        while True:
            try:
                ws = await self._connect_ws()
                logger.info("connected to stt")
                tasks = [
                    asyncio.create_task(send_task(ws)),
                    asyncio.create_task(recv_task(ws)),
                ]
                wait_reconnect_task = asyncio.create_task(self._reconnect_event.wait())
                try:
                    done, _ = await asyncio.wait(
                        [asyncio.gather(*tasks), wait_reconnect_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )  # type: ignore
                    # propagate exceptions from completed tasks
                    for task in done:
                        if task != wait_reconnect_task:
                            task.result()

                    if wait_reconnect_task not in done:
                        break

                    self._reconnect_event.clear()
                finally:
                    await utils.aio.gracefully_cancel(*tasks, wait_reconnect_task)
            finally:
                if ws is not None:
                    await ws.close()

    def _process_stream_event_paraformer(self, data: dict) -> None:
        data = data["data"]
        state = data[
            "state"
        ]  # segment_start, segment_end, interim_transcript, final_transcript
        text = data["text"]
        start_time = data["start_time"]
        end_time = data["end_time"]
        logger.debug(f"received paraformer message state: {state}")
        if state == "final_transcript":
            alts = [
                stt.SpeechData(
                    language="zh-CN",
                    text=text,
                    start_time=start_time,
                    end_time=end_time,
                )
            ]
        else:
            alts = [stt.SpeechData(language="zh-CN", text=text)]
        if state == "segment_start":
            self._speaking = True
            start_event = stt.SpeechEvent(
                type=stt.SpeechEventType.START_OF_SPEECH,
                request_id=self._request_id,
                # alternatives=alts,
            )
            self._event_ch.send_nowait(start_event)
            logger.info("transcription start")
        if state == "interim_transcript":
            event = stt.SpeechEvent(
                type=stt.SpeechEventType.INTERIM_TRANSCRIPT,
                alternatives=alts,
                request_id=self._request_id,
            )
            self._event_ch.send_nowait(event)
        if state == "final_transcript":
            event = stt.SpeechEvent(
                type=stt.SpeechEventType.FINAL_TRANSCRIPT,
                alternatives=alts,
                request_id=self._request_id,
            )
            self._event_ch.send_nowait(event)
            logger.info(
                "transcription end",
                extra={"text": text, "start_time": start_time, "end_time": end_time},
            )
        if state == "segment_end":
            end_event = stt.SpeechEvent(
                type=stt.SpeechEventType.END_OF_SPEECH,
                request_id=self._request_id,
                # alternatives=alts,
            )
            self._event_ch.send_nowait(end_event)

    async def _run_aliyun(self) -> None:
        closing_ws = False

        @utils.log_exceptions(logger=logger)
        async def send_task(ws: aiohttp.ClientWebSocketResponse):
            nonlocal closing_ws

            samples_50ms = self._opts.sample_rate // 20
            audio_bstream = utils.audio.AudioByteStream(
                sample_rate=self._opts.sample_rate,
                num_channels=1,
                samples_per_channel=samples_50ms,
            )

            has_ended = False
            async for frame in self._input_ch:
                frames: list[rtc.AudioFrame] = []
                if isinstance(frame, rtc.AudioFrame):
                    frames.extend(audio_bstream.write(frame.data.tobytes()))
                elif isinstance(frame, self._FlushSentinel):
                    frames.extend(audio_bstream.flush())
                    has_ended = True

                for frame in frames:
                    self._audio_duration_collector.push(frame.duration)
                    await ws.send_bytes(frame.data.tobytes())

                    if has_ended:
                        self._audio_duration_collector.flush()
                        await ws.send_str("close")
                        has_ended = False
                        closing_ws = True
                        logger.info("closing stt ws")
                        await ws.close()

        @utils.log_exceptions(logger=logger)
        async def recv_task(ws: aiohttp.ClientWebSocketResponse):
            nonlocal closing_ws
            while True:
                msg = await ws.receive()
                if msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSING,
                ):
                    if closing_ws:  # close is expected, see SpeechStream.aclose
                        return

                    # this will trigger a reconnection, see the _run loop
                    logger.error("connection closed unexpectedly")
                    break

                try:
                    self._process_stream_event_aliyun(json.loads(msg.data))
                except Exception:
                    logger.exception("failed to process deepgram message")

        ws: aiohttp.ClientWebSocketResponse | None = None

        while True:
            try:
                ws = await self._connect_ws()
                logger.info("connected to stt")
                tasks = [
                    asyncio.create_task(send_task(ws)),
                    asyncio.create_task(recv_task(ws)),
                ]
                wait_reconnect_task = asyncio.create_task(self._reconnect_event.wait())
                try:
                    done, _ = await asyncio.wait(
                        [asyncio.gather(*tasks), wait_reconnect_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )  # type: ignore
                    # propagate exceptions from completed tasks
                    for task in done:
                        if task != wait_reconnect_task:
                            task.result()

                    if wait_reconnect_task not in done:
                        break

                    self._reconnect_event.clear()
                finally:
                    await utils.aio.gracefully_cancel(*tasks, wait_reconnect_task)
            finally:
                if ws is not None:
                    await ws.close()

    async def _connect_ws(self) -> aiohttp.ClientWebSocketResponse:
        ws = await asyncio.wait_for(
            self._session.ws_connect(self._opts.get_ws_url()),
            self._conn_options.timeout,
        )
        return ws

    def _on_audio_duration_report(self, duration: float) -> None:
        usage_event = stt.SpeechEvent(
            type=stt.SpeechEventType.RECOGNITION_USAGE,
            request_id=self._request_id,
            alternatives=[],
            recognition_usage=stt.RecognitionUsage(audio_duration=duration),
        )
        self._event_ch.send_nowait(usage_event)

    def _process_stream_event_aliyun(self, data: dict) -> None:
        state = data["header"][
            "name"
        ]  # SentenceBegin, SentenceEnd, TranscriptionResultChanged
        if state == "SentenceBegin":
            self._speaking = True
            start_event = stt.SpeechEvent(
                type=stt.SpeechEventType.START_OF_SPEECH, request_id=self._request_id
            )
            self._event_ch.send_nowait(start_event)
            logger.info("transcription start")
        if state == "TranscriptionResultChanged":
            text = data["payload"]["result"]
            alts = [stt.SpeechData(language="zh-CN", text=text)]
            event = stt.SpeechEvent(
                type=stt.SpeechEventType.INTERIM_TRANSCRIPT,
                alternatives=alts,
                request_id=self._request_id,
            )
            self._event_ch.send_nowait(event)
        if state == "SentenceEnd":
            text = data["payload"]["result"]
            end_time = data["payload"]["time"]
            start_time = data["payload"]["begin_time"]
            confidence = data["payload"]["confidence"]
            alts = [
                stt.SpeechData(
                    language="zh-CN",
                    text=text,
                    start_time=start_time,
                    end_time=end_time,
                    confidence=confidence,
                )
            ]
            event = stt.SpeechEvent(
                type=stt.SpeechEventType.FINAL_TRANSCRIPT,
                alternatives=alts,
                request_id=self._request_id,
            )
            self._event_ch.send_nowait(event)
            end_event = stt.SpeechEvent(
                type=stt.SpeechEventType.END_OF_SPEECH, request_id=self._request_id
            )
            self._event_ch.send_nowait(end_event)
            logger.info("transcription end", extra={"text": text})


T = TypeVar("T")


class PeriodicCollector(Generic[T]):
    def __init__(self, callback: Callable[[T], None], *, duration: float) -> None:
        """
        Create a new periodic collector that accumulates values and calls the callback
        after the specified duration if there are values to report.

        Args:
            duration: Time in seconds between callback invocations
            callback: Function to call with accumulated value when duration expires
        """
        self._duration = duration
        self._callback = callback
        self._last_flush_time = time.monotonic()
        self._total: Optional[T] = None

    def push(self, value: T) -> None:
        """Add a value to the accumulator"""
        if self._total is None:
            self._total = value
        else:
            self._total += value  # type: ignore
        if time.monotonic() - self._last_flush_time >= self._duration:
            self.flush()

    def flush(self) -> None:
        """Force callback to be called with current total if non-zero"""
        if self._total is not None:
            self._callback(self._total)
            self._total = None
        self._last_flush_time = time.monotonic()
