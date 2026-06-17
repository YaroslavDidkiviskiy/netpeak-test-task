import asyncio

from google import genai
from google.genai import types
from google.genai.errors import APIError
from app.config import get_settings
from app.models import Category, Priority

CLASSIFICATION_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    required=[
        "category", "target_department", "priority",
        "short_summary", "requested_actions", "needs_clarification",
    ],
    properties={
        "category": types.Schema(
            type=types.Type.STRING,
            enum=[e.value for e in Category]
        ),
        "target_department": types.Schema(type=types.Type.STRING),
        "priority": types.Schema(
            type=types.Type.STRING,
            enum=list(e.value for e in Priority)
        ),
        "short_summary": types.Schema(type=types.Type.STRING),
        "requested_actions": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING),
        ),
        "needs_clarification": types.Schema(type=types.Type.BOOLEAN),
    },
)


class GeminiClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self.model = "gemini-2.5-flash"

    async def classify(self, prompt: str, retries: int = 3) -> str:
        for attempt in range(retries):
            try:
                response = await self._client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=CLASSIFICATION_SCHEMA,
                        temperature=0.1,
                        max_output_tokens=1024,
                    ),
                )
                return response.text or "{}"
            except APIError as e:
                if e.code == 429 and attempt < retries - 1:
                    await asyncio.sleep(10 * (attempt + 1))
                else:
                    raise
        raise RuntimeError("Gemini rate limit exceeded after retries")
