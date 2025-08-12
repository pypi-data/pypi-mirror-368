import boto3

from llmhub.core.secret_managers.base import BaseSecretManager


class AWSSecretManager(BaseSecretManager):
    def __init__(self, region_name: str = "us-east-1"):
        self.client = boto3.client("secretsmanager", region_name=region_name)

    def get_secret(self, name: str) -> str:
        response = self.client.get_secret_value(SecretId=name)
        return response.get("SecretString", "")
