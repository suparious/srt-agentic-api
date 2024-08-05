from fastapi import APIRouter, HTTPException, Depends, Query
from uuid import UUID
from typing import Optional
import json
from datetime import datetime
from app.api.models.memory import MemoryType, MemorySearchRequest, MemorySearchResponse, AdvancedSearchQuery
from app.utils.auth import get_api_key
from app.utils.logging import memory_logger
from .utils import get_memory_system

router = APIRouter()

@router.post("/search", response_model=MemorySearchResponse, summary="Search memory entries")
async def search_memory_endpoint(request: MemorySearchRequest, api_key: str = Depends(get_api_key)):
    """
    Search memory entries for an agent using basic search criteria.

    Parameters:
    - **request**: MemorySearchRequest object containing:
        - agent_id: UUID of the agent
        - memory_type: Type of memory to search (SHORT_TERM, LONG_TERM, or None for both)
        - query: Search query string
        - limit: Maximum number of results to return

    Returns:
    - **MemorySearchResponse**: Object containing:
        - agent_id: UUID of the agent
        - results: List of matching MemoryEntry objects
        - relevance_scores: List of relevance scores for each result

    Raises:
    - **500 Internal Server Error**: If there's an unexpected error during the process
    """
    try:
        memory_logger.info(f"Searching memories for agent: {request.agent_id}")
        memory_system = await get_memory_system(request.agent_id)
        query = AdvancedSearchQuery(
            query=request.query,
            memory_type=request.memory_type,
            max_results=request.limit
        )
        results = await memory_system.search(query)
        memory_logger.info(f"Memory search completed for agent: {request.agent_id}")
        return MemorySearchResponse(
            agent_id=request.agent_id,
            results=[result["memory_entry"] for result in results],
            relevance_scores=[result["relevance_score"] for result in results]
        )
    except Exception as e:
        memory_logger.error(f"Error searching memories for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/advanced-search", response_model=MemorySearchResponse, summary="Advanced search memory entries")
async def advanced_search_memory_endpoint(
        agent_id: UUID,
        query: str = Query(..., description="The main search query"),
        memory_type: Optional[MemoryType] = Query(None, description="Type of memory to search"),
        context_type: Optional[str] = Query(None, description="The type of context to search within"),
        time_range_start: Optional[str] = Query(None, description="Start of time range (ISO format)"),
        time_range_end: Optional[str] = Query(None, description="End of time range (ISO format)"),
        metadata_filters: Optional[str] = Query(None, description="JSON string of metadata filters"),
        relevance_threshold: Optional[float] = Query(None, ge=0, le=1, description="Minimum relevance score"),
        max_results: int = Query(10, ge=1, description="Maximum number of results to return"),
        api_key: str = Depends(get_api_key)
):
    """
    Perform an advanced search on memory entries for an agent.

    This endpoint allows for more complex queries with various filters and parameters.

    Parameters:
    - **agent_id**: UUID of the agent to search memories for
    - **query**: The main search query string
    - **memory_type**: Type of memory to search (SHORT_TERM, LONG_TERM, or None for both)
    - **context_type**: The type of context to search within
    - **time_range_start**: Start of time range in ISO format (e.g., "2023-05-01T00:00:00")
    - **time_range_end**: End of time range in ISO format
    - **metadata_filters**: JSON string of metadata filters (e.g., '{"key": "value"}')
    - **relevance_threshold**: Minimum relevance score for results (0 to 1)
    - **max_results**: Maximum number of results to return

    Returns:
    - **MemorySearchResponse**: Object containing:
        - agent_id: UUID of the agent
        - results: List of matching MemoryEntry objects
        - relevance_scores: List of relevance scores for each result

    Raises:
    - **400 Bad Request**: If the query parameters are invalid
    - **500 Internal Server Error**: If there's an unexpected error during the process
    """
    try:
        memory_logger.info(f"Performing advanced search for agent: {agent_id}")
        memory_system = await get_memory_system(agent_id)

        time_range = None
        if time_range_start and time_range_end:
            time_range = {
                "start": datetime.fromisoformat(time_range_start),
                "end": datetime.fromisoformat(time_range_end)
            }

        metadata_filters_dict = json.loads(metadata_filters) if metadata_filters else None

        advanced_query = AdvancedSearchQuery(
            query=query,
            memory_type=memory_type,
            context_type=context_type,
            time_range=time_range,
            metadata_filters=metadata_filters_dict,
            relevance_threshold=relevance_threshold,
            max_results=max_results
        )

        results = await memory_system.search(advanced_query)
        memory_logger.info(f"Advanced memory search completed for agent: {agent_id}")
        return MemorySearchResponse(
            agent_id=agent_id,
            results=[result["memory_entry"] for result in results],
            relevance_scores=[result["relevance_score"] for result in results]
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        memory_logger.error(f"Error performing advanced search for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
