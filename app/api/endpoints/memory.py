from fastapi import APIRouter, HTTPException, Depends, Query
from uuid import UUID
from typing import List, Optional
from app.api.models.memory import (
    MemoryType, MemoryEntry, MemoryAddRequest, MemoryAddResponse,
    MemoryRetrieveRequest, MemoryRetrieveResponse, MemorySearchRequest,
    MemorySearchResponse, MemoryDeleteRequest, MemoryDeleteResponse,
    MemoryOperationRequest, MemoryOperationResponse, AdvancedSearchQuery
)
from app.core.memory import (
    get_memory_system, add_to_memory, retrieve_from_memory,
    search_memory, delete_from_memory, perform_memory_operation
)
from app.core.agent import get_agent_memory_config
from app.utils.auth import get_api_key
from app.utils.logging import memory_logger

router = APIRouter()

@router.post("/add", response_model=MemoryAddResponse, status_code=201, summary="Add a memory entry")
async def add_memory_endpoint(request: MemoryAddRequest, api_key: str = Depends(get_api_key)):
    """
    Add a new memory entry for an agent.

    Parameters:
    - **request**: MemoryAddRequest object containing:
        - agent_id: UUID of the agent
        - memory_type: Type of memory (SHORT_TERM or LONG_TERM)
        - entry: MemoryEntry object with content, metadata, and context

    Returns:
    - **MemoryAddResponse**: Object containing:
        - agent_id: UUID of the agent
        - memory_id: Unique identifier for the added memory
        - message: Success message

    Raises:
    - **400 Bad Request**: If the memory type or configuration is invalid
    - **500 Internal Server Error**: If there's an unexpected error during the process
    """
    try:
        memory_logger.info(f"Adding memory for agent: {request.agent_id}")
        memory_config = await get_agent_memory_config(request.agent_id)
        memory_id = await add_to_memory(request.agent_id, request.memory_type, request.entry, memory_config)
        memory_logger.info(f"Memory added successfully for agent: {request.agent_id}")
        return MemoryAddResponse(
            agent_id=request.agent_id,
            memory_id=memory_id,
            message="Memory added successfully"
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        memory_logger.error(f"Error adding memory for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/retrieve", response_model=MemoryRetrieveResponse, summary="Retrieve a memory entry")
async def retrieve_memory_endpoint(request: MemoryRetrieveRequest = Depends(), api_key: str = Depends(get_api_key)):
    """
    Retrieve a specific memory entry for an agent.

    Parameters:
    - **request**: MemoryRetrieveRequest object containing:
        - agent_id: UUID of the agent
        - memory_type: Type of memory (SHORT_TERM or LONG_TERM)
        - memory_id: Unique identifier of the memory to retrieve

    Returns:
    - **MemoryRetrieveResponse**: Object containing:
        - agent_id: UUID of the agent
        - memory: Retrieved MemoryEntry object

    Raises:
    - **404 Not Found**: If the requested memory entry is not found
    - **500 Internal Server Error**: If there's an unexpected error during the process
    """
    try:
        memory_logger.info(f"Retrieving memory for agent: {request.agent_id}")
        memory_config = await get_agent_memory_config(request.agent_id)
        memory = await retrieve_from_memory(request.agent_id, request.memory_type, request.memory_id, memory_config)
        if memory is None:
            raise HTTPException(status_code=404, detail="Memory not found")
        memory_logger.info(f"Memory retrieved successfully for agent: {request.agent_id}")
        return MemoryRetrieveResponse(
            agent_id=request.agent_id,
            memory=memory
        )
    except HTTPException:
        raise
    except Exception as e:
        memory_logger.error(f"Error retrieving memory for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
        memory_config = await get_agent_memory_config(request.agent_id)
        query = AdvancedSearchQuery(
            query=request.query,
            memory_type=request.memory_type,
            max_results=request.limit
        )
        results = await search_memory(request.agent_id, query, memory_config)
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
        memory_config = await get_agent_memory_config(agent_id)

        # Convert time range strings to datetime objects if provided
        time_range = None
        if time_range_start and time_range_end:
            from datetime import datetime
            time_range = {
                "start": datetime.fromisoformat(time_range_start),
                "end": datetime.fromisoformat(time_range_end)
            }

        # Parse metadata filters if provided
        metadata_filters_dict = None
        if metadata_filters:
            import json
            metadata_filters_dict = json.loads(metadata_filters)

        advanced_query = AdvancedSearchQuery(
            query=query,
            memory_type=memory_type,
            context_type=context_type,
            time_range=time_range,
            metadata_filters=metadata_filters_dict,
            relevance_threshold=relevance_threshold,
            max_results=max_results
        )

        results = await search_memory(agent_id, advanced_query, memory_config)
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

@router.delete("/delete", response_model=MemoryDeleteResponse, summary="Delete a memory entry")
async def delete_memory_endpoint(request: MemoryDeleteRequest, api_key: str = Depends(get_api_key)):
    """
    Delete a specific memory entry for an agent.

    Parameters:
    - **request**: MemoryDeleteRequest object containing:
        - agent_id: UUID of the agent
        - memory_type: Type of memory (SHORT_TERM or LONG_TERM)
        - memory_id: Unique identifier of the memory to delete

    Returns:
    - **MemoryDeleteResponse**: Object containing:
        - agent_id: UUID of the agent
        - message: Success message

    Raises:
    - **500 Internal Server Error**: If there's an unexpected error during the process
    """
    try:
        memory_logger.info(f"Deleting memory for agent: {request.agent_id}")
        memory_config = await get_agent_memory_config(request.agent_id)
        await delete_from_memory(request.agent_id, request.memory_type, request.memory_id, memory_config)
        memory_logger.info(f"Memory deleted successfully for agent: {request.agent_id}")
        return MemoryDeleteResponse(
            agent_id=request.agent_id,
            message="Memory deleted successfully"
        )
    except Exception as e:
        memory_logger.error(f"Error deleting memory for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/operate", response_model=MemoryOperationResponse, summary="Perform a memory operation")
async def memory_operation_endpoint(request: MemoryOperationRequest, api_key: str = Depends(get_api_key)):
    """
    Perform a generic memory operation for an agent.

    This endpoint allows for various memory operations to be performed based on the operation type specified in the request.

    Parameters:
    - **request**: MemoryOperationRequest object containing:
        - agent_id: UUID of the agent
        - operation: Type of memory operation to perform (ADD, RETRIEVE, SEARCH, DELETE)
        - memory_type: Type of memory (SHORT_TERM or LONG_TERM)
        - data: Additional data required for the operation (varies based on operation type)

    Returns:
    - **MemoryOperationResponse**: Object containing:
        - agent_id: UUID of the agent
        - operation: The performed operation
        - result: Result of the operation (varies based on operation type)
        - message: Success message

    Raises:
    - **400 Bad Request**: If the operation or parameters are invalid
    - **500 Internal Server Error**: If there's an unexpected error during the process
    """
    try:
        memory_logger.info(f"Performing {request.operation} operation for agent: {request.agent_id}")
        memory_config = await get_agent_memory_config(request.agent_id)
        result = await perform_memory_operation(request.agent_id, request.operation, request.memory_type, request.data,
                                                memory_config)
        memory_logger.info(f"{request.operation} operation completed for agent: {request.agent_id}")
        return MemoryOperationResponse(
            agent_id=request.agent_id,
            operation=request.operation,
            result=result,
            message=f"{request.operation} operation completed successfully"
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        memory_logger.error(f"Error performing {request.operation} operation for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
