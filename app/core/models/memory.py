from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4


class MemoryConfig(BaseModel):
    use_long_term_memory: bool = Field(..., description="Whether to use long-term memory storage for the agent")
    use_redis_cache: bool = Field(..., description="Whether to use Redis for short-term memory caching")

    model_config = ConfigDict(extra="forbid")

class MemoryContext(BaseModel):
    context_type: str = Field(..., description="The type of context for the memory")
    timestamp: datetime = Field(..., description="The timestamp of the memory context")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata for the context"
    )

    model_config = ConfigDict(extra="forbid")

class MemoryEntry(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    content: str = Field(..., description="The content of the memory")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional metadata associated with the memory"
    )
    context: MemoryContext = Field(..., description="The context of the memory entry")

    model_config = ConfigDict(extra="forbid")
