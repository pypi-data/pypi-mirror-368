from llmhub.core.secret_managers.base import BaseSecretManager


class BaseClientAsync:
    def __init__(self, secret_manager: BaseSecretManager, warnings: bool = False):
        self.warnings = warnings

    async def create_response():
        pass

    async def get_response():
        pass

    async def delete_response():
        pass

    async def cancel_response():
        pass

    async def list_response_input():
        pass

    async def create_batch():
        pass

    async def get_batch():
        pass

    async def cancel_batch():
        pass

    async def list_batch():
        pass
