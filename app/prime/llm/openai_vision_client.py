# app/prime/llm/openai_vision_client.py
import base64
import os
from openai import AsyncOpenAI


class OpenAIVisionClient:
    def __init__(self):
        self._client = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
        return self._client

    async def describe_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str = "What do you see in this image?",
    ) -> str:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        client = self._get_client()
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{b64}",
                                "detail": "auto",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content or ""


openai_vision_client = OpenAIVisionClient()
