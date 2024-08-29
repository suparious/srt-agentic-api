from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum
from app.api.models.memory import MemoryType


class AgentMessageRequest(BaseModel):
    agent_id: UUID = Field(
        ..., description="The unique identifier of the agent to send the message to"
    )
    message: str = Field(..., description="The message content to send to the agent")
    
    model_config = ConfigDict(extra="forbid")


class AgentMessageResponse(BaseModel):
    agent_id: UUID = Field(
        ..., description="The unique identifier of the agent that processed the message"
    )
    response: str = Field(..., description="The agent's response to the input message")
    function_calls: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Any function calls the agent wants to make in response to the message",
    )

    model_config = ConfigDict(extra="forbid")


class AgentFunctionRequest(BaseModel):
    agent_id: UUID = Field(
        ...,
        description="The unique identifier of the agent to execute the function for",
    )
    function_name: str = Field(
        ..., description="The name of the function to be executed"
    )
    parameters: Dict[str, Any] = Field(
        ..., description="The parameters to be passed to the function"
    )

    model_config = ConfigDict(extra="forbid")


class AgentFunctionResponse(BaseModel):
    agent_id: UUID = Field(
        ..., description="The unique identifier of the agent that executed the function"
    )
    result: Any = Field(..., description="The result returned by the executed function")

    model_config = ConfigDict(extra="forbid")


class MemoryOperation(str, Enum):
    ADD = "add"
    RETRIEVE = "retrieve"
    SEARCH = "search"


class AgentMemoryRequest(BaseModel):
    agent_id: UUID = Field(
        ...,
        description="The unique identifier of the agent to perform the memory operation for",
    )
    operation: MemoryOperation = Field(
        ..., description="The type of memory operation to perform"
    )
    memory_type: MemoryType = Field(
        ..., description="The type of memory to operate on (SHORT_TERM or LONG_TERM)"
    )
    data: Optional[Dict[str, Any]] = Field(
        None, description="The data to be added or retrieved in memory operations"
    )
    query: Optional[str] = Field(
        None, description="The search query for memory search operations"
    )

    model_config = ConfigDict(extra="forbid")


class AgentMemoryResponse(BaseModel):
    agent_id: UUID = Field(
        ...,
        description="The unique identifier of the agent the memory operation was performed for",
    )
    result: Any = Field(..., description="The result of the memory operation")

    model_config = ConfigDict(extra="forbid")

class AgentDeleteResponse(BaseModel):
    agent_id: UUID = Field(
        ..., description="The unique identifier of the deleted agent"
    )
    message: str = Field(
        ..., description="A message indicating the result of the agent deletion process"
    )

    model_config = ConfigDict(extra="forbid")
