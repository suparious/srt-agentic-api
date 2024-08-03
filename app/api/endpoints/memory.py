from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List
from app.api.models.memory import (
    MemoryType,
    MemoryEntry,
    MemoryAddRequest,
    MemoryAddResponse,
    MemoryRetrieveRequest,
    MemoryRetrieveResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryDeleteRequest,
    MemoryDeleteResponse,
    MemoryOperationRequest,
    MemoryOperationResponse,
    AdvancedSearchQuery
)
from app.core.memory import (
    add_to_memory,
    retrieve_from_memory,
    search_memory,
    delete_from_memory,
    perform_memory_operation
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
    - **request**: MemoryAddRequest object containing agent_id, memory_type, and entry details

    Returns:
    - **MemoryAddResponse**: Object containing agent_id, memory_id, and a success message

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
    - **request**: MemoryRetrieveRequest object containing agent_id, memory_type, and memory_id

    Returns:
    - **MemoryRetrieveResponse**: Object containing agent_id and the retrieved memory entry

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
    Search memory entries for an agent.

    Parameters:
    - **request**: MemorySearchRequest object containing agent_id, memory_type, query, and limit

    Returns:
    - **MemorySearchResponse**: Object containing agent_id and a list of matching memory entries

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
async def advanced_search_memory_endpoint(request: AdvancedSearchQuery, agent_id: UUID, api_key: str = Depends(get_api_key)):
    """
    Perform an advanced search on memory entries for an agent.

    Parameters:
    - **request**: AdvancedSearchQuery object containing detailed search parameters
    - **agent_id**: UUID of the agent to search memories for

    Returns:
    - **MemorySearchResponse**: Object containing agent_id, list of matching memory entries, and relevance scores

    Raises:
    - **500 Internal Server Error**: If there's an unexpected error during the process
    """
    try:
        memory_logger.info(f"Performing advanced search for agent: {agent_id}")
        memory_config = await get_agent_memory_config(agent_id)
        results = await search_memory(agent_id, request, memory_config)
        memory_logger.info(f"Advanced memory search completed for agent: {agent_id}")
        return MemorySearchResponse(
            agent_id=agent_id,
            results=[result["memory_entry"] for result in results],
            relevance_scores=[result["relevance_score"] for result in results]
        )
    except Exception as e:
        memory_logger.error(f"Error performing advanced search for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete", response_model=MemoryDeleteResponse, summary="Delete a memory entry")
async def delete_memory_endpoint(request: MemoryDeleteRequest, api_key: str = Depends(get_api_key)):
    """
    Delete a specific memory entry for an agent.

    Parameters:
    - **request**: MemoryDeleteRequest object containing agent_id, memory_type, and memory_id

    Returns:
    - **MemoryDeleteResponse**: Object containing agent_id and a success message

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

    Parameters:
    - **request**: MemoryOperationRequest object containing agent_id, operation, memory_type, and operation data

    Returns:
    - **MemoryOperationResponse**: Object containing agent_id, operation performed, operation result, and a success message

    Raises:
    - **500 Internal Server Error**: If there's an unexpected error during the process
    """
    try:
        memory_logger.info(f"Performing {request.operation} operation for agent: {request.agent_id}")
        memory_config = await get_agent_memory_config(request.agent_id)
        result = await perform_memory_operation(request.agent_id, request.operation, request.memory_type, request.data, memory_config)
        memory_logger.info(f"{request.operation} operation completed for agent: {request.agent_id}")
        return MemoryOperationResponse(
            agent_id=request.agent_id,
            operation=request.operation,
            result=result,
            message=f"{request.operation} operation completed successfully"
        )
    except Exception as e:
        memory_logger.error(f"Error performing {request.operation} operation for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
