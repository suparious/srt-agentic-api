from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum

class MemoryConfig(BaseModel):
    use_long_term_memory: bool = Field(..., description="Whether to use long-term memory storage for the agent")
    use_redis_cache: bool = Field(..., description="Whether to use Redis for short-term memory caching")

class AgentConfig(BaseModel):
    llm_provider: str = Field(..., description="The LLM provider to use for this agent (e.g., 'openai', 'anthropic', 'huggingface')")
    model_name: str = Field(..., description="The specific model name to use (e.g., 'gpt-4', 'claude-v1')")
    temperature: float = Field(..., ge=0.0, le=1.0, description="The temperature setting for the LLM, controlling randomness in outputs")
    max_tokens: int = Field(..., gt=0, description="The maximum number of tokens the LLM should generate in a single response")
    memory_config: MemoryConfig = Field(..., description="Configuration settings for the agent's memory systems")

    model_config = ConfigDict(protected_namespaces=())

class AgentCreationRequest(BaseModel):
    agent_name: str = Field(..., description="The name of the agent to be created")
    agent_config: AgentConfig = Field(..., description="Configuration settings for the agent's language model")
    memory_config: MemoryConfig = Field(..., description="Configuration settings for the agent's memory systems")
    initial_prompt: str = Field(..., description="The initial prompt or instructions to provide to the agent upon creation")

class AgentCreationResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier assigned to the newly created agent")
    message: str = Field(..., description="A message indicating the result of the agent creation process")

class AgentMessageRequest(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent to send the message to")
    message: str = Field(..., description="The message content to send to the agent")

class AgentMessageResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent that processed the message")
    response: str = Field(..., description="The agent's response to the input message")
    function_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Any function calls the agent wants to make in response to the message")

class AgentFunctionRequest(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent to execute the function for")
    function_name: str = Field(..., description="The name of the function to be executed")
    parameters: Dict[str, Any] = Field(..., description="The parameters to be passed to the function")

class AgentFunctionResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent that executed the function")
    result: Any = Field(..., description="The result returned by the executed function")

class MemoryOperation(str, Enum):
    ADD = "add"
    RETRIEVE = "retrieve"
    SEARCH = "search"

class AgentMemoryRequest(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent to perform the memory operation for")
    operation: MemoryOperation = Field(..., description="The type of memory operation to perform")
    data: Optional[Dict[str, Any]] = Field(None, description="The data to be added or retrieved in memory operations")
    query: Optional[str] = Field(None, description="The search query for memory search operations")

class AgentMemoryResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent the memory operation was performed for")
    result: Any = Field(..., description="The result of the memory operation")

class AgentInfoResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent")
    name: str = Field(..., description="The name of the agent")
    config: AgentConfig = Field(..., description="The current configuration of the agent's language model")
    memory_config: MemoryConfig = Field(..., description="The current configuration of the agent's memory systems")
    conversation_history_length: int = Field(..., description="The number of messages in the agent's conversation history")

class AgentUpdateRequest(BaseModel):
    agent_config: Optional[AgentConfig] = Field(None, description="Updated configuration for the agent's language model")
    memory_config: Optional[MemoryConfig] = Field(None, description="Updated configuration for the agent's memory systems")

class AgentUpdateResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the updated agent")
    message: str = Field(..., description="A message indicating the result of the agent update process")

class AgentDeleteResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the deleted agent")
    message: str = Field(..., description="A message indicating the result of the agent deletion process")
