from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class OpenAIService:
    """Small wrapper around the OpenAI Responses and Embeddings APIs."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5.4",
        embedding_model: str = "text-embedding-3-small",
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing.")
        self.client = OpenAI(
            api_key=api_key,
            timeout=180.0,
            max_retries=2,
        )
        self.model = model
        self.embedding_model = embedding_model

    def parse(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[T],
        reasoning_effort: str = "medium",
        max_output_tokens: int = 10_000,
    ) -> T:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            reasoning={"effort": reasoning_effort},
            text_format=schema,
            max_output_tokens=max_output_tokens,
            store=False,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError("The model returned no structured output.")
        return parsed

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        cleaned = [text.strip() or "empty" for text in texts]
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=cleaned,
            encoding_format="float",
        )
        ordered = sorted(response.data, key=lambda item: item.index)
        return [item.embedding for item in ordered]
