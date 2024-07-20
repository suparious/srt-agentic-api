from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum

class AgentConfig(BaseModel):
    llm_provider: str
    model_name: str
    temperature: float = Field(ge=0.0, le=1.0)
    max_tokens: int = Field(gt=0)

class MemoryConfig(BaseModel):
    use_long_term_memory: bool = True
    use_redis_cache: bool = True

class AgentCreationRequest(BaseModel):
    agent_name: str
    agent_config: AgentConfig
    memory_config: MemoryConfig
    initial_prompt: str

class AgentCreationResponse(BaseModel):
    agent_id: UUID
    message: str

class AgentMessageRequest(BaseModel):
    agent_id: UUID
    message: str

class AgentMessageResponse(BaseModel):
    agent_id: UUID
    response: str
    function_calls: Optional[List[Dict[str, Any]]]

class AgentFunctionRequest(BaseModel):
    agent_id: UUID
    function_name: str
    parameters: Dict[str, Any]

class AgentFunctionResponse(BaseModel):
    agent_id: UUID
    result: Any

class MemoryOperation(str, Enum):
    ADD = "add"
    RETRIEVE = "retrieve"
    SEARCH = "search"

class AgentMemoryRequest(BaseModel):
    agent_id: UUID
    operation: MemoryOperation
    data: Optional[Dict[str, Any]]
    query: Optional[str]

class AgentMemoryResponse(BaseModel):
    agent_id: UUID
    result: Any

class AgentInfoResponse(BaseModel):
    agent_id: UUID
    name: str
    config: AgentConfig
    memory_config: MemoryConfig
    conversation_history_length: int

class AgentUpdateRequest(BaseModel):
    agent_config: Optional[AgentConfig] = None
    memory_config: Optional[MemoryConfig] = None

class AgentUpdateResponse(BaseModel):
    agent_id: UUID
    message: str

class AgentDeleteResponse(BaseModel):
    agent_id: UUID
    message: str
