from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
import requests

import aiohttp
from livekit.agents import (
    APIConnectionError,
    APIStatusError,
    llm,
)
from livekit.agents.types import (
    DEFAULT_API_CONNECT_OPTIONS,
    APIConnectOptions,
    NotGivenOr,
    NOT_GIVEN,
)
from livekit.agents.llm import FunctionTool, ToolChoice

from .log import logger


@dataclass
class LLMOptions:
    api_key: str
    api_base: str = "https://dify.58corp.com/v1"
    user: str | None = None
    _conversation_id: str | None = None
    end_char: str = ""

    def get_parameters_url(self) -> str:
        return f"{self.api_base}/parameters"

    def get_message_history_url(self) -> str:
        return f"{self.api_base}/messages"

    def get_conversation_history_url(self) -> str:
        return f"{self.api_base}/conversations"

    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }


class Dify(llm.LLM):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_base: str = "https://dify.58corp.com/v1",
        user: str | None = None,
        use_last_conversation: bool = False,
        max_last_conversation_time: int = 1,
        end_words: List[str] = [],
    ) -> None:
        """
        Create a new instance of Dify LLM.

        api_key (str | None): The Dify API key. Defaults to DIFY_API_KEY env var.
        api_base (str | None): The base URL for the Dify API. Defaults to https://dify.58corp.com/v1
        user (str | None): The user identifier for the LLM. Defaults to None.
        use_last_conversation (bool): Whether to use the last conversation ID if available.
            If True, it will attempt to fetch the last conversation ID and use it for the new
            conversation. If no previous conversation is found, it will start a new one.
        max_last_conversation_time (int): The maximum time in hours to look back for the last conversation.
        end_words (List[str]): 结束关键词,会触发end_call工具。
        """
        super().__init__()
        self._session: Optional[aiohttp.ClientSession] = None

        api_key = api_key or os.environ.get("DIFY_API_KEY")
        if api_key is None:
            raise ValueError("Dify API key is required")

        logger.info(f"api_key: {api_key}")
        self._opts = LLMOptions(api_key=api_key, api_base=api_base, user=user)
        self._end_words = end_words

        if use_last_conversation:
            last_conversation_id = self.get_last_conversation_id(
                max_last_conversation_time=max_last_conversation_time
            )
            if last_conversation_id:
                self._opts._conversation_id = last_conversation_id
                logger.info(f"Using last conversation ID: {last_conversation_id}")
            else:
                logger.warning("No previous conversation found, starting a new one.")

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        tools: list[FunctionTool] | None = None,
        parallel_tool_calls: NotGivenOr[bool] = NOT_GIVEN,
        tool_choice: NotGivenOr[ToolChoice] = NOT_GIVEN,
        extra_kwargs: NotGivenOr[dict[str, Any]] = NOT_GIVEN,
    ) -> "LLMStream":
        """Start a chat completion stream"""
        # Extract the last user message
        query_contents = []
        for msg in chat_ctx.items[::-1]:
            if msg.role != "user":
                break
            else:
                query_contents.append(msg.content[0])
        query_contents.reverse()
        query = "".join(query_contents)
        # Prepare the request payload
        payload = {
            "inputs": {},
            "query": query,
            "response_mode": "streaming",
            "conversation_id": self._opts._conversation_id,
            "user": self._opts.user,
        }
        # Create headers
        headers = {
            "Authorization": f"Bearer {self._opts.api_key}",
            "Content-Type": "application/json",
        }

        # Create or reuse the session
        if self._session is None:
            self._session = aiohttp.ClientSession()
        logger.info("llm start", extra={"query": query})
        # Create the stream
        stream = self._session.post(
            f"{self._opts.api_base}/chat-messages", headers=headers, json=payload
        )

        return LLMStream(
            self,
            dify_stream=stream,
            chat_ctx=chat_ctx,
            conn_options=conn_options,
            tools=tools,
            end_words=self._end_words,
        )

    def ensure_session(self) -> None:
        """Ensure that the session is created"""
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def get_parameters(self) -> Dict:
        """Get the parameters for the LLM"""
        self.ensure_session()
        res = await self._session.get(
            url=self._opts.get_parameters_url(), headers=self._opts.get_headers()
        )
        return await res.json()

    async def get_opening_words(self) -> str:
        """Get the introduction text for the LLM"""
        params = await self.get_parameters()
        return params.get("opening_statement", "")

    async def is_chatable(self) -> bool:
        """Check if the LLM is chatable"""
        url = self._opts.get_conversation_history_url()
        url = f"{url}?&user={self._opts.user}"
        self.ensure_session()
        res = await self._session.get(url=url, headers=self._opts.get_headers())
        if res.status != 200:
            return False
        return True

    def get_last_conversation_id(
        self, max_last_conversation_time: int = 1
    ) -> Optional[str]:
        """Get the last conversation ID"""
        url = self._opts.get_conversation_history_url()
        url = f"{url}?&user={self._opts.user}"
        try:
            response = requests.get(url, headers=self._opts.get_headers())
            if response.status_code == 200:
                conversations = response.json()["data"]
                if conversations:
                    last_conversation = conversations[0]
                    last_conversation_id = last_conversation.get("id")
                    last_conversation_time: int = last_conversation.get(
                        "updated_at"
                    )  # timestamp of the last conversation, eg 1679667915
                    # Check if the last conversation is within the allowed time
                    if last_conversation_time:
                        last_conversation_datetime = datetime.fromtimestamp(
                            last_conversation_time
                        )
                        if datetime.now() - last_conversation_datetime < timedelta(
                            hours=max_last_conversation_time
                        ):
                            return last_conversation_id
                        else:
                            logger.info(
                                "Last conversation is too old, starting a new one."
                            )
            else:
                logger.error(f"Error fetching conversations: {response.text}")
        except requests.RequestException as e:
            logger.error(f"Error fetching last conversation ID: {e}")
        return None

    async def required_inputs(self) -> bool:
        """Check if the LLM requires inputs"""
        paras = await self.get_parameters()
        user_input_form = paras.get("user_input_form", [])
        if len(user_input_form) == 0:
            return False
        else:
            required = False
            for item in user_input_form:
                key = list(item.items())[0][0]
                _item = item.get(key, {})
                required = _item.get("required", False)
                break
            return required

    async def close(self) -> None:
        """Close the LLM client and cleanup resources"""
        if self._session is not None:
            await self._session.close()
            self._session = None

    @classmethod
    def from_env(cls) -> "Dify":
        """Create a DifyLLM instance from environment variables"""
        api_key = os.getenv("DIFY_API_KEY")
        if not api_key:
            raise ValueError("DIFY_API_KEY environment variable is required")

        api_base = os.getenv("DIFY_API_BASE", "https://dify.58corp.com/v1")

        return cls(
            api_key=api_key,
            api_base=api_base,
        )


class LLMStream(llm.LLMStream):
    def __init__(
        self,
        llm: Dify,
        *,
        dify_stream: aiohttp.ClientResponse,
        chat_ctx: llm.ChatContext,
        conn_options: APIConnectOptions,
        end_words: List[str],
        tools: list[FunctionTool] | None = None,
    ) -> None:
        super().__init__(llm, chat_ctx=chat_ctx, conn_options=conn_options, tools=tools)
        self._awaitable_dify_stream = dify_stream
        self._dify_stream: aiohttp.ClientResponse | None = None
        self._request_id: str = ""
        self._input_tokens = 0
        self._output_tokens = 0
        self._end_words = end_words

    async def _run(self) -> None:
        """Run the LLM stream"""
        # is_chatable = await self._llm.is_chatable()
        # required_inputs = await self._llm.required_inputs()
        # is_available = is_chatable and (not required_inputs)
        # if not is_available:
        #     error_text = "Dify is not available"
        #     raise APIConnectionError(error_text, retryable=False)

        retryable = True
        first_response = True
        final_text = ""
        try:
            if not self._dify_stream:
                self._dify_stream = await self._awaitable_dify_stream
            async with self._dify_stream as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise APIStatusError(
                        f"Dify API error: {error_text}",
                        status_code=response.status,
                        body=error_text,
                    )
                async for line in response.content:
                    if line:
                        try:
                            line = line.decode("utf-8").strip()
                            if line.startswith("data: "):
                                data = json.loads(line[6:])
                                chat_chunk = await self._parse_event(
                                    data, self._llm._opts
                                )
                                if chat_chunk is not None:
                                    final_text += chat_chunk.delta.content
                                    self._event_ch.send_nowait(chat_chunk)
                                    retryable = False
                                    if first_response:
                                        logger.info("llm first response")
                                        first_response = False
                        except Exception as e:
                            logger.error(f"Error processing stream: {e}")
                            continue

                for end_word in self._end_words:
                    if end_word in final_text:
                        self._event_ch.send_nowait(
                            llm.ChatChunk(
                                id=self._request_id,
                                usage=llm.CompletionUsage(
                                    completion_tokens=self._output_tokens,
                                    prompt_tokens=self._input_tokens,
                                    total_tokens=self._input_tokens
                                    + self._output_tokens,
                                ),
                                delta=llm.ChoiceDelta(
                                    role="assistant",
                                    content="",
                                    tool_calls=[
                                        llm.FunctionToolCall(
                                            arguments="",
                                            name="end_call",  # type: ignore
                                            call_id="",
                                        )
                                    ],
                                ),
                            )
                        )
                        logger.info(f"end word: {end_word} found, select end-call tool")
                logger.info("llm end")

        except aiohttp.ClientError as e:
            raise APIConnectionError(retryable=retryable) from e
        except Exception as e:
            raise APIConnectionError(retryable=retryable) from e

    async def _parse_event(
        self, event: Dict[str, Any], ops: LLMOptions
    ) -> llm.ChatChunk | None:
        """Parse a Dify event into a ChatChunk"""
        event_type = event.get("event")
        if event_type == "agent_message" or event_type == "message":
            if ops._conversation_id is None:
                ops._conversation_id = event.get("conversation_id", None)
            # Extract message content
            answer = event.get("answer", "")
            if answer == "" and ops.end_char:
                logger.info(f"llm send end char: {ops.end_char}")
                return llm.ChatChunk(
                    id=event.get("message_id", ""),
                    delta=llm.ChoiceDelta(
                        role="assistant",
                        content=ops.end_char,
                    ),
                )
            return llm.ChatChunk(
                id=event.get("message_id", ""),
                delta=llm.ChoiceDelta(
                    role="assistant",
                    content=answer,
                ),
            )

        return None
