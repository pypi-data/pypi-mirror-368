from abc import ABC, abstractmethod


class BaseSecretManager(ABC):
    @abstractmethod
    def get_secret(self, name: str) -> str:
        """Retrieve the secret value by name."""
        pass
