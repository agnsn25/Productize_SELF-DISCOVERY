import asyncio

from google import genai
from google.genai import types

from .config import settings


class GeminiClient:
    def __init__(self):
        self._client = None
        self.model = settings.gemini_model

    @property
    def client(self):
        if self._client is None:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    async def generate(
        self,
        prompt: str,
        thinking_budget: int = -1,
        json_schema: dict | None = None,
        include_thoughts: bool = True,
    ) -> dict:
        """Call Gemini and return {"text": str, "thoughts": str | None}.

        The underlying SDK call is synchronous, so we run it in a thread
        to avoid blocking the async event loop.
        """
        config_kwargs: dict = {
            "thinking_config": types.ThinkingConfig(
                thinking_budget=thinking_budget,
                include_thoughts=include_thoughts,
            )
        }

        if json_schema is not None:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = json_schema

        config = types.GenerateContentConfig(**config_kwargs)

        # Run the synchronous SDK call in a worker thread.
        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model,
            contents=prompt,
            config=config,
        )

        thoughts: list[str] = []
        text_parts: list[str] = []

        for part in response.candidates[0].content.parts:
            if part.thought:
                thoughts.append(part.text)
            else:
                text_parts.append(part.text)

        usage = {}
        um = getattr(response, "usage_metadata", None)
        if um is not None:
            usage = {
                "input_tokens": getattr(um, "prompt_token_count", 0) or 0,
                "output_tokens": getattr(um, "candidates_token_count", 0) or 0,
                "thinking_tokens": getattr(um, "thoughts_token_count", 0) or 0,
                "total_tokens": getattr(um, "total_token_count", 0) or 0,
            }

        return {
            "text": "\n".join(text_parts),
            "thoughts": "\n".join(thoughts) if thoughts else None,
            "usage": usage,
        }


gemini = GeminiClient()
