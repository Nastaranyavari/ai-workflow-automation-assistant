import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class OpenRouterProvider:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv(
            "OPENROUTER_MODEL",
            "openrouter/free",
        )

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not set."
            )

        self._model = model

        self._client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def generate(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content or ""

    def chat(self, messages: list, tools: list | None = None):
        return self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None,
        )