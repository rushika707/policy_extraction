import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class LLMClient:

    def __init__(self, model=None, base_url=None):

        self.model = model or os.getenv(
            "LLM_MODEL"
        )

        self.base_url = base_url or os.getenv(
            "LLM_BASE_URL",
            "http://localhost:11434/v1"
        )

        if not self.model:
            raise ValueError(
                "LLM_MODEL is not configured in .env"
            )

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=os.getenv(
                "LLM_API_KEY",
                "ollama"
            )
        )

    def generate(
        self,
        prompt,
        temperature=0,
        max_tokens=8192
    ):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        if not content:
            raise ValueError(
                "LLM returned an empty response."
            )

        return content