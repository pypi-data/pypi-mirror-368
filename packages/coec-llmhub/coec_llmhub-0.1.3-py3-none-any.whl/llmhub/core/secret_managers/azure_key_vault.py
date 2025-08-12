from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from llmhub.core.secret_managers.base import BaseSecretManager


class AzureKeyVault(BaseSecretManager):
    def __init__(self, vault_url: str):
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=vault_url, credential=credential)

    def get_secret(self, name: str) -> str:
        secret = self.client.get_secret(name)
        return secret.value
