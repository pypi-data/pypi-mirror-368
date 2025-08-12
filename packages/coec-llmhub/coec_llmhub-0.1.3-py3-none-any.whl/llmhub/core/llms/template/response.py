from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class BaseGenerationModel(BaseModel):
    model: str = Field(..., description="The name of the model to use")
    messages: Any = Field(...)
    system: Optional[str] = Field("", description="")
    max_tokens: Optional[int] = Field(None)
    response_schema: Optional[Any] = Field(None)


class ErrorObject(BaseModel):
    message: str = Field(..., description="Error message.")
    type: Optional[str] = Field(None, description="Error type.")
    code: Optional[str] = Field(None, description="Error code.")


class IncompleteDetails(BaseModel):
    reason: Optional[str] = Field(
        None, description="Reason why the response is incomplete."
    )


class Reasoning(BaseModel):
    mode: Optional[str] = Field(
        None, description="Configuration option for o-series reasoning models."
    )


class PromptReference(BaseModel):
    template_id: Optional[str] = Field(
        None, description="Reference ID for a prompt template."
    )
    variables: Optional[Dict[str, Any]] = Field(
        None, description="Variables used in the template."
    )


class BaseGenerationResponseModel(BaseModel):
    background: Optional[bool] = Field(
        None,
        description="Whether to run the model response in the background.",
        example=False,
    )
    created_at: int = Field(
        ...,
        description="Unix timestamp (in seconds) of response creation.",
        example=1722230400,
    )
    error: Optional[ErrorObject] = Field(
        None, description="An error object if the model failed."
    )
    id: Optional[str] = Field(
        str, description="Unique identifier for this Response.", example="resp_abc123"
    )
    incomplete_details: Optional[IncompleteDetails] = Field(
        None, description="Why the response was incomplete."
    )
    instructions: Union[str, List[str]] = Field(
        ...,
        description="System/developer instructions for the model.",
        example="You are a helpful assistant.",
    )
    max_output_tokens: Optional[int] = Field(
        None, description="Maximum tokens allowed in output.", example=500
    )
    max_tool_calls: Optional[int] = Field(
        None, description="Maximum number of tool calls allowed.", example=2
    )
    metadata: Optional[Dict[str, str]] = Field(
        None,
        description="Key-value metadata (up to 16 pairs).",
        example={"session_id": "abc123"},
    )
    model: str = Field(..., description="ID of the model used.", example="gpt-4o")
    object: str = Field(
        ..., description="Object type, always 'response'.", example="response"
    )
    output: List[Any] = Field(
        ..., description="Generated content items from the model."
    )
    output_text: Optional[str] = Field(
        None,
        description="Aggregated text output from all content items.",
        example="Hello! How can I help you?",
    )
    parallel_tool_calls: Optional[bool] = Field(
        None, description="Allow parallel tool calls.", example=True
    )
    previous_response_id: Optional[str] = Field(
        None, description="ID of the previous response.", example="resp_prev456"
    )
    prompt: Optional[PromptReference] = Field(
        None, description="Reference to a prompt template and its variables."
    )
    prompt_cache_key: Optional[str] = Field(
        None,
        description="Key used for caching similar prompts.",
        example="cache_key_xyz789",
    )
    reasoning: Optional[Reasoning] = Field(
        None, description="Reasoning config for o-series models."
    )
    safety_identifier: Optional[str] = Field(
        None,
        description="Stable identifier to detect policy violations.",
        example="user_hash_123",
    )
    service_tier: Optional[str] = Field(
        None, description="Processing tier used.", example="default"
    )
    status: str = Field(..., description="Generation status.", example="completed")
    temperature: Optional[float] = Field(
        None, description="Sampling temperature (0 to 2).", example=0.7
    )
    text: Optional[Dict[str, Any]] = Field(
        None, description="Text response configuration.", example={"format": "plain"}
    )
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(
        None, description="Tool selection strategy.", example="auto"
    )
    tools: Optional[List[Dict[str, Any]]] = Field(
        None, description="Array of tool definitions."
    )
    top_logprobs: Optional[int] = Field(
        None,
        description="Number of top log probabilities to return per token.",
        example=5,
    )
    top_p: Optional[float] = Field(
        None, description="Top-p (nucleus) sampling probability.", example=0.9
    )
    truncation: Optional[str] = Field(
        None, description="Truncation strategy.", example="auto"
    )
    usage: Optional[Dict[str, Any]] = Field(
        None,
        description="Token usage breakdown.",
        example={"input_tokens": 10, "output_tokens": 20},
    )
