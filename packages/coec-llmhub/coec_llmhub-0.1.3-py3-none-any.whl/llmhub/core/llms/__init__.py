from typing import List, Literal

from llmhub.core.secret_managers.base import BaseSecretManager
from llmhub.core.secret_managers.env_var_secrets import EnvSecretManager

from .anthropic import AnthropicClientAsync
from .gemini import GeminiClientAsync
from .template.response import BaseGenerationModel

CLIENT_FACTORY_ASYNC = {"anthropic": AnthropicClientAsync, "gemini": GeminiClientAsync}


class LLMClientAsync:
    def __init__(
        self,
        providers: List[Literal["gemini", "anthropic"]] = ["gemini"],
        secret_manager: BaseSecretManager = EnvSecretManager(),
    ):
        assert isinstance(providers, list)
        self.clients = {}
        for provider in providers:
            if provider in CLIENT_FACTORY_ASYNC.keys():
                self.clients[provider] = CLIENT_FACTORY_ASYNC[provider](secret_manager)
            else:
                print(provider)
                # TODO Warn user here

    async def create_generation(self, input_model: BaseGenerationModel, provider: str):
        assert provider in self.clients.keys()
        return await self.clients[provider].create_generation(input_model)
