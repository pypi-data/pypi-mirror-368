from typing import Literal, Optional

try:
    from anthropic import AsyncClient
except ImportError:
    pass

from pydantic import BaseModel, Field

from llmhub.core.llms.template import BaseClientAsync
from llmhub.core.llms.template.response import (
    BaseGenerationModel,
    BaseGenerationResponseModel,
)
from llmhub.core.secret_managers.base import BaseSecretManager


class PDFDocumentPart(BaseModel):
    type: Optional[str] = Field("base64")
    media_type: Optional[str] = Field("application/pdf")
    data: str = Field(...)


class Part(BaseModel):
    """A datatype containing media content.

    Exactly one field within a Part should be set, representing the specific type
    of content being conveyed. Using multiple fields within the same `Part`
    instance is considered invalid.
    """

    type: Literal[
        "document",
        "image",
        "redacted_thinking",
        "server_tool_use",
        "text",
        "thinking",
        "tool_result",
        "tool_use",
        "web_search_tool_result",
    ] = Field(...)

    text: Optional[str] = Field(
        default=None, description="""Optional. Text part (can be code)."""
    )

    source: Optional[PDFDocumentPart] = Field(None)

    @classmethod
    def from_text(cls, *, text: str, **args) -> "Part":
        part = cls(text=text, type="text").dict()
        return {k: v for k, v in part.items() if v is not None}

    @classmethod
    def from_base64(cls, *, file_data: str, **args) -> "Part":
        part = cls(type="document", source=PDFDocumentPart(data=file_data)).dict()
        return {k: v for k, v in part.items() if v is not None}


class AnthropicClientAsync(BaseClientAsync):
    def __init__(self, secret_manager: BaseSecretManager):
        self.client = AsyncClient(
            api_key=secret_manager.get_secret("ANTHROPIC_API_KEY")
        )
        self.PART_TYPE_CACTORY = {
            "text": Part.from_text,
            "input_file": Part.from_base64,
        }

    def format_content(self, messages):
        return [
            {
                "role": content["role"],
                "content": [
                    self.PART_TYPE_CACTORY[part["type"]](**part)
                    for part in content["content"]
                ],
            }
            for content in messages
        ]

    async def create_generation(self, input_model: BaseGenerationModel):
        response = await self.client.messages.create(
            model=input_model.model,
            max_tokens=input_model.max_tokens,
            messages=self.format_content(input_model.messages),
        )

        parsed_response = BaseGenerationResponseModel(
            created_at=int(0),
            instructions=input_model.system,
            model=response.model,
            object="response",
            output=[
                {
                    "content": [
                        {
                            "annotations": [],
                            "text": j.text,
                            "type": "output_text",
                            "logprobs": [],
                        }
                        for j in response.content
                    ],
                    "id": response.id,
                    "role": response.role,
                    "status": "completed",
                    "type": "message",
                }
            ],
            status="completed",
        )
        return parsed_response
