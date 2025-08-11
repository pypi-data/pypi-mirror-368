import os
from typing import Type

from pydantic import BaseModel
from litellm import completion


class LLMClient:
    def __init__(
        self,
        model: str,
        api_key: str,
        response_format: Type[BaseModel]
    ) -> None:
        os.environ[self._get_provider_name(model)] = api_key
        self.model = model
        self.response_format = response_format

    def predict(self, message: str) -> str:
        response = completion(
            model=self.model,
            messages=[{'content': message, 'role': 'user'}],
            response_format=self.response_format
        )
        return response.choices[0].message.content

    @staticmethod
    def _get_provider_name(model_name: str) -> str:
        if model_name.startswith('claude'):
            return 'ANTHROPIC_API_KEY'
        if model_name.startswith(('openai', 'gpt')):
            return 'OPENAI_API_KEY'
        if model_name.startswith('deepseek'):
            return 'DEEPSEEK_API_KEY'
        raise ValueError('Передан некорректный провайдер')
