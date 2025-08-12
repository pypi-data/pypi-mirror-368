import os

from llmhub.core.secret_managers.base import BaseSecretManager


class EnvSecretManager(BaseSecretManager):
    def get_secret(self, name: str) -> str:
        value = os.getenv(name)
        if value is None:
            raise KeyError(f"Environment variable '{name}' not found")
        return value
