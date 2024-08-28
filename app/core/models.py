from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional, Callable
from uuid import UUID, uuid4
from enum import Enum

class LLMProviderConfig(BaseModel):
    provider_type: str = Field(..., description="The LLM provider type (e.g., 'openai', 'vllm', 'llamacpp', 'tgi')")
    model_name: str = Field(..., description="The specific model name to use (e.g., 'gpt-4', 'claude-v1')")
    api_key: Optional[str] = Field(None, description="API key for the provider (if required)")
    api_base: Optional[str] = Field(None, description="Base URL for the provider's API (if custom)")

    model_config = ConfigDict(extra="forbid")

class MemoryConfig(BaseModel):
    use_long_term_memory: bool = Field(..., description="Whether to use long-term memory storage for the agent")
    use_redis_cache: bool = Field(..., description="Whether to use Redis for short-term memory caching")

    model_config = ConfigDict(extra="forbid")

class AgentConfig(BaseModel):
    llm_providers: List[LLMProviderConfig] = Field(..., min_length=1, description="List of LLM provider configurations")
    temperature: float = Field(..., ge=0.0, le=1.0, description="The temperature setting for the LLM, controlling randomness in outputs")
    max_tokens: int = Field(..., gt=0, description="The maximum number of tokens the LLM should generate in a single response")
    memory_config: MemoryConfig = Field(..., description="Configuration settings for the agent's memory systems")

    model_config = ConfigDict(extra="forbid")

class AgentCreationRequest(BaseModel):
    agent_name: str = Field(..., description="The name of the agent to be created")
    agent_config: AgentConfig = Field(..., description="Configuration settings for the agent's language model")
    memory_config: MemoryConfig = Field(..., description="Configuration settings for the agent's memory systems")
    initial_prompt: str = Field(..., description="The initial prompt or instructions to provide to the agent upon creation")

    model_config = ConfigDict(extra="forbid")

class AgentCreationResponse(BaseModel):
    agent_id: UUID = Field(
        ..., description="The unique identifier assigned to the newly created agent"
    )
    message: str = Field(
        ..., description="A message indicating the result of the agent creation process"
    )

    model_config = ConfigDict(extra="forbid")

class AgentInfoResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent")
    name: str = Field(..., description="The name of the agent")
    config: AgentConfig = Field(
        ..., description="The current configuration of the agent's language model"
    )
    memory_config: MemoryConfig = Field(
        ..., description="The current configuration of the agent's memory systems"
    )
    conversation_history_length: int = Field(
        ..., description="The number of messages in the agent's conversation history"
    )

    model_config = ConfigDict(extra="forbid")

class AgentUpdateRequest(BaseModel):
    agent_config: Optional[AgentConfig] = Field(
        None, description="Updated configuration for the agent's language model"
    )
    memory_config: Optional[MemoryConfig] = Field(
        None, description="Updated configuration for the agent's memory systems"
    )

    model_config = ConfigDict(extra="forbid")


class AgentUpdateResponse(BaseModel):
    agent_id: UUID = Field(
        ..., description="The unique identifier of the updated agent"
    )
    message: str = Field(
        ..., description="A message indicating the result of the agent update process"
    )

    model_config = ConfigDict(extra="forbid")

class FunctionDefinition(BaseModel):
    """
    Represents the definition of a function that can be called by an agent.
    """

    id: UUID = Field(
        default_factory=uuid4, description="The unique identifier of the function"
    )
    name: str = Field(
        ..., description="The name of the function", example="calculate_sum"
    )
    description: str = Field(
        ...,
        description="A brief description of what the function does",
        example="Calculates the sum of two numbers",
    )
    parameters: Dict[str, Any] = Field(
        ...,
        description="The parameters the function accepts",
        example={"a": {"type": "number"}, "b": {"type": "number"}},
    )
    return_type: str = Field(
        ..., description="The type of value the function returns", example="number"
    )
    implementation: Optional[Callable] = Field(
        None, description="The actual implementation of the function"
    )

    model_config = ConfigDict(
        extra="forbid",
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "calculate_sum",
                "description": "Calculates the sum of two numbers",
                "parameters": {"a": {"type": "number"}, "b": {"type": "number"}},
                "return_type": "number",
            }
        },
    )