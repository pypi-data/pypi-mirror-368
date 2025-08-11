"""OpenAI client for Mind Terminal."""
from openai import OpenAI

from mindterm.config import config


class LLMClient:
    """Client for interacting with the LLM."""

    def __init__(self) -> None:
        """Initialize the LLM client."""
        if not config.validate():
            raise ValueError(
                "Invalid configuration. Please set the OPENAI_API_KEY environment variable."
            )

        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )
        self.model = config.model

    def get_completion(self, content: str) -> str | None:
        """Get completion from the LLM."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": content},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting completion: {e}")
            return None
