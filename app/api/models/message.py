from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID


class MessageRequest(BaseModel):
    """
    Represents a request to send a message to an agent.
    """

    agent_id: UUID = Field(
        ..., description="The ID of the agent to send the message to"
    )
    content: str = Field(..., description="The content of the message")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional metadata associated with the message"
    )


class FunctionCall(BaseModel):
    """
    Represents a function call made by the agent.
    """

    name: str = Field(..., description="The name of the function to call")
    arguments: Dict[str, Any] = Field(
        ..., description="The arguments for the function call"
    )


class MessageResponse(BaseModel):
    """
    Represents the response from an agent after processing a message.
    """

    agent_id: UUID = Field(
        ..., description="The ID of the agent that processed the message"
    )
    content: str = Field(..., description="The content of the agent's response")
    function_calls: Optional[List[FunctionCall]] = Field(
        default=None, description="Any function calls the agent wants to make"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional metadata associated with the response"
    )


class MessageHistoryRequest(BaseModel):
    """
    Represents a request to retrieve message history for an agent.
    """

    agent_id: UUID = Field(
        ..., description="The ID of the agent to retrieve history for"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="The maximum number of messages to retrieve",
    )
    before: Optional[str] = Field(
        default=None, description="Retrieve messages before this timestamp"
    )


class MessageHistoryItem(BaseModel):
    """
    Represents a single item in the message history.
    """

    id: str = Field(..., description="Unique identifier for the message")
    timestamp: str = Field(
        ..., description="Timestamp of when the message was sent or received"
    )
    sender: str = Field(
        ..., description="Identifier of the sender (e.g., 'user' or 'agent')"
    )
    content: str = Field(..., description="Content of the message")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional metadata associated with the message"
    )


class MessageHistoryResponse(BaseModel):
    """
    Represents the response containing message history for an agent.
    """

    agent_id: UUID = Field(..., description="The ID of the agent")
    messages: List[MessageHistoryItem] = Field(
        ..., description="List of messages in the history"
    )
    has_more: bool = Field(
        ..., description="Indicates if there are more messages that can be retrieved"
    )
