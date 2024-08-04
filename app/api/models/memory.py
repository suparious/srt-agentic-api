from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional
from uuid import UUID
from enum import Enum
from datetime import datetime

class MemoryType(str, Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"

class MemoryOperation(str, Enum):
    ADD = "add"
    RETRIEVE = "retrieve"
    SEARCH = "search"
    DELETE = "delete"

class MemoryContext(BaseModel):
    context_type: str = Field(..., description="The type of context for the memory")
    timestamp: datetime = Field(..., description="The timestamp of the memory context")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the context")

    model_config = ConfigDict(extra='forbid')

class MemoryEntry(BaseModel):
    content: str = Field(..., description="The content of the memory")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata associated with the memory")
    context: MemoryContext = Field(..., description="The context of the memory entry")

    model_config = ConfigDict(extra='forbid')

class AdvancedSearchQuery(BaseModel):
    query: str = Field(..., description="The main search query")
    memory_type: Optional[MemoryType] = Field(None, description="The type of memory to search (SHORT_TERM, LONG_TERM, or both if None)")
    time_range: Optional[Dict[str, datetime]] = Field(None, description="The time range to search within (e.g., {'start': datetime, 'end': datetime})")
    context_type: Optional[str] = Field(None, description="The type of context to search within")
    metadata_filters: Optional[Dict[str, Any]] = Field(None, description="Filters to apply on metadata")
    relevance_threshold: Optional[float] = Field(None, ge=0, le=1, description="The minimum relevance score for results (0 to 1)")
    max_results: int = Field(default=10, ge=1, description="The maximum number of results to return")

    model_config = ConfigDict(extra='forbid')

class MemoryAddRequest(BaseModel):
    agent_id: UUID = Field(..., description="The ID of the agent to add the memory for")
    memory_type: MemoryType = Field(..., description="The type of memory (short-term or long-term)")
    entry: MemoryEntry = Field(..., description="The memory entry to add")

    model_config = ConfigDict(extra='forbid')

class MemoryAddResponse(BaseModel):
    agent_id: UUID = Field(..., description="The ID of the agent")
    memory_id: str = Field(..., description="The unique identifier assigned to the added memory")
    message: str = Field(..., description="A message indicating the result of the operation")

    model_config = ConfigDict(extra='forbid')

class MemoryRetrieveRequest(BaseModel):
    agent_id: UUID = Field(..., description="The ID of the agent to retrieve the memory for")
    memory_type: MemoryType = Field(..., description="The type of memory (short-term or long-term)")
    memory_id: str = Field(..., description="The unique identifier of the memory to retrieve")

    model_config = ConfigDict(extra='forbid')

class MemoryRetrieveResponse(BaseModel):
    agent_id: UUID = Field(..., description="The ID of the agent")
    memory: MemoryEntry = Field(..., description="The retrieved memory entry")

    model_config = ConfigDict(extra='forbid')

class MemorySearchRequest(BaseModel):
    agent_id: UUID = Field(..., description="The ID of the agent to search memories for")
    memory_type: MemoryType = Field(..., description="The type of memory to search (short-term or long-term)")
    query: str = Field(..., description="The search query")
    limit: int = Field(default=10, ge=1, le=100, description="The maximum number of results to return")

    model_config = ConfigDict(extra='forbid')

class MemorySearchResponse(BaseModel):
    agent_id: UUID = Field(..., description="The ID of the agent")
    results: List[MemoryEntry] = Field(..., description="The list of memory entries matching the search query")
    relevance_scores: Optional[List[float]] = Field(None, description="The relevance scores for each result, if calculated")

    model_config = ConfigDict(extra='forbid')

class MemoryDeleteRequest(BaseModel):
    agent_id: UUID = Field(..., description="The ID of the agent to delete the memory for")
    memory_type: MemoryType = Field(..., description="The type of memory (short-term or long-term)")
    memory_id: str = Field(..., description="The unique identifier of the memory to delete")

    model_config = ConfigDict(extra='forbid')

class MemoryDeleteResponse(BaseModel):
    agent_id: UUID = Field(..., description="The ID of the agent")
    message: str = Field(..., description="A message indicating the result of the deletion")

    model_config = ConfigDict(extra='forbid')

class MemoryOperationRequest(BaseModel):
    agent_id: UUID = Field(..., description="The ID of the agent")
    operation: MemoryOperation = Field(..., description="The memory operation to perform")
    memory_type: MemoryType = Field(..., description="The type of memory (short-term or long-term)")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Data required for the operation")

    model_config = ConfigDict(extra='forbid')

class MemoryOperationResponse(BaseModel):
    agent_id: UUID = Field(..., description="The ID of the agent")
    operation: MemoryOperation = Field(..., description="The memory operation that was performed")
    result: Any = Field(..., description="The result of the memory operation")
    message: Optional[str] = Field(default=None, description="An optional message about the operation")

    model_config = ConfigDict(extra='forbid')
