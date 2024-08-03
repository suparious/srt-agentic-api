from pydantic import BaseModel, Field
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

class MemoryEntry(BaseModel):
    """
    Represents a single memory entry.
    """
    content: str = Field(..., description="The content of the memory")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata associated with the memory")

class AdvancedSearchQuery(BaseModel):
    """
    Represents an advanced search query for memory entries.
    """
    query: str = Field(..., description="The main search query")
    memory_type: Optional[MemoryType] = Field(None,
                                              description="The type of memory to search (SHORT_TERM, LONG_TERM, or both if None)")
    time_range: Optional[Dict[str, datetime]] = Field(None,
                                                      description="The time range to search within (e.g., {'start': datetime, 'end': datetime})")
    context_type: Optional[str] = Field(None, description="The type of context to search within")
    metadata_filters: Optional[Dict[str, Any]] = Field(None, description="Filters to apply on metadata")
    relevance_threshold: Optional[float] = Field(None, ge=0, le=1,
                                                 description="The minimum relevance score for results (0 to 1)")
    max_results: int = Field(default=10, ge=1, description="The maximum number of results to return")

class MemoryAddRequest(BaseModel):
    """
    Represents a request to add a memory for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to add the memory for")
    memory_type: MemoryType = Field(..., description="The type of memory (short-term or long-term)")
    entry: MemoryEntry = Field(..., description="The memory entry to add")

class MemoryAddResponse(BaseModel):
    """
    Represents the response after adding a memory.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    memory_id: str = Field(..., description="The unique identifier assigned to the added memory")
    message: str = Field(..., description="A message indicating the result of the operation")

class MemoryRetrieveRequest(BaseModel):
    """
    Represents a request to retrieve a specific memory for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to retrieve the memory for")
    memory_type: MemoryType = Field(..., description="The type of memory (short-term or long-term)")
    memory_id: str = Field(..., description="The unique identifier of the memory to retrieve")

class MemoryRetrieveResponse(BaseModel):
    """
    Represents the response containing a retrieved memory.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    memory: MemoryEntry = Field(..., description="The retrieved memory entry")

class MemorySearchRequest(BaseModel):
    """
    Represents a request to search memories for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to search memories for")
    memory_type: MemoryType = Field(..., description="The type of memory to search (short-term or long-term)")
    query: str = Field(..., description="The search query")
    limit: int = Field(default=10, ge=1, le=100, description="The maximum number of results to return")

class MemorySearchResponse(BaseModel):
    """
    Represents the response containing search results from memory.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    results: List[MemoryEntry] = Field(..., description="The list of memory entries matching the search query")
    relevance_scores: Optional[List[float]] = Field(None, description="The relevance scores for each result, if calculated")

class MemoryDeleteRequest(BaseModel):
    """
    Represents a request to delete a specific memory for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to delete the memory for")
    memory_type: MemoryType = Field(..., description="The type of memory (short-term or long-term)")
    memory_id: str = Field(..., description="The unique identifier of the memory to delete")

class MemoryDeleteResponse(BaseModel):
    """
    Represents the response after deleting a memory.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    message: str = Field(..., description="A message indicating the result of the deletion")

class MemoryOperationRequest(BaseModel):
    """
    Represents a generic memory operation request.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    operation: MemoryOperation = Field(..., description="The memory operation to perform")
    memory_type: MemoryType = Field(..., description="The type of memory (short-term or long-term)")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Data required for the operation")

class MemoryOperationResponse(BaseModel):
    """
    Represents a generic memory operation response.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    operation: MemoryOperation = Field(..., description="The memory operation that was performed")
    result: Any = Field(..., description="The result of the memory operation")
    message: Optional[str] = Field(default=None, description="An optional message about the operation")
