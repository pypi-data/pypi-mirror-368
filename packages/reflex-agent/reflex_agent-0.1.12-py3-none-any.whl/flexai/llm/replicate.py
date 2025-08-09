from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncGenerator

from flexai.llm.client import Client
from flexai.message import AIMessage, Message, MessageContent, SystemMessage
from flexai.tool import Tool

# Try to import the replicate library.
try:
    import replicate  # type: ignore
except ImportError:
    raise ImportError(
        "The replicate library is required for the ReplicateClient. "
        "Please install it using `pip install replicate`."
    )


@dataclass(frozen=True)
class ReplicateClient(Client):
    model: str

    async def get_chat_response(
        self,
        messages: list[Message] = [],
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        **kwargs,
    ) -> AIMessage:
        if isinstance(system, str):
            system = SystemMessage(content=system)
        try:
            output = list(
                replicate.run(  # type: ignore
                    self.model,
                    input={
                        "prompt": system.content,
                    },
                )
            )
        except Exception:
            output = []

        return AIMessage(
            content=output,
        )

    async def stream_chat_response(
        self,
        messages: list[Message] = [],
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        allow_tool: bool = True,
        **kwargs,
    ) -> AsyncGenerator[MessageContent | AIMessage, None]:
        if False:
            yield
        raise NotImplementedError(
            "stream_chat_response is not implemented for replicate client."
        )
