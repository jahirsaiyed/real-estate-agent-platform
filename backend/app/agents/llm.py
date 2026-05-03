from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.messages import BaseMessage

from app.core.config import settings


class LLMProvider:
    """Model-agnostic LLM interface. Swap model via LLM_MODEL_ID env var."""

    def __init__(self) -> None:
        self.model_id = settings.LLM_MODEL_ID
        self._client = self._build_client()

    def _build_client(self) -> Any:
        model_id = self.model_id.lower()

        if "gemma" in model_id or "/" in model_id:
            # Route via OpenRouter (OpenAI-compatible endpoint)
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=self.model_id,
                openai_api_key=settings.OPENROUTER_API_KEY,
                openai_api_base="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://real-estate-agent.app",
                    "X-Title": "Real Estate Agent",
                },
            )
        elif "claude" in model_id:
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(model=self.model_id)
        elif "gpt" in model_id:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=self.model_id)
        else:
            # Default: try OpenRouter
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=self.model_id,
                openai_api_key=settings.OPENROUTER_API_KEY,
                openai_api_base="https://openrouter.ai/api/v1",
            )

    async def ainvoke(self, messages: list[BaseMessage], **kwargs: Any) -> BaseMessage:
        return await self._client.ainvoke(messages, **kwargs)

    async def astream(
        self, messages: list[BaseMessage], **kwargs: Any
    ) -> AsyncGenerator[BaseMessage, None]:
        async for chunk in self._client.astream(messages, **kwargs):
            yield chunk


# Module-level singleton
llm_provider = LLMProvider()
