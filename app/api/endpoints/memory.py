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
    MemoryOperationResponse
)
from app.core.memory import (
    add_to_memory,
    retrieve_from_memory,
    search_memory,
    delete_from_memory,
    perform_memory_operation
)
from app.core.agent import get_agent_memory_config  # Assuming this function exists to get MemoryConfig for an agent
from app.utils.auth import get_api_key
from app.utils.logging import memory_logger

router = APIRouter()

@router.post("/add", response_model=MemoryAddResponse, summary="Add a memory entry")
async def add_memory_endpoint(
    request: MemoryAddRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Add a new memory entry for an agent.

    - **agent_id**: The ID of the agent to add the memory for
    - **memory_type**: The type of memory (short-term or long-term)
    - **entry**: The memory entry to add
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
    except Exception as e:
        memory_logger.error(f"Error adding memory for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/retrieve", response_model=MemoryRetrieveResponse, summary="Retrieve a memory entry")
async def retrieve_memory_endpoint(
    request: MemoryRetrieveRequest = Depends(),
    api_key: str = Depends(get_api_key)
):
    """
    Retrieve a specific memory entry for an agent.

    - **agent_id**: The ID of the agent to retrieve the memory for
    - **memory_type**: The type of memory (short-term or long-term)
    - **memory_id**: The unique identifier of the memory to retrieve
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
async def search_memory_endpoint(
    request: MemorySearchRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Search memory entries for an agent.

    - **agent_id**: The ID of the agent to search memories for
    - **memory_type**: The type of memory to search (short-term or long-term)
    - **query**: The search query
    - **limit**: The maximum number of results to return
    """
    try:
        memory_logger.info(f"Searching memories for agent: {request.agent_id}")
        memory_config = await get_agent_memory_config(request.agent_id)
        results = await search_memory(request.agent_id, request.memory_type, request.query, request.limit, memory_config)
        memory_logger.info(f"Memory search completed for agent: {request.agent_id}")
        return MemorySearchResponse(
            agent_id=request.agent_id,
            results=results
        )
    except Exception as e:
        memory_logger.error(f"Error searching memories for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete", response_model=MemoryDeleteResponse, summary="Delete a memory entry")
async def delete_memory_endpoint(
    request: MemoryDeleteRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Delete a specific memory entry for an agent.

    - **agent_id**: The ID of the agent to delete the memory for
    - **memory_type**: The type of memory (short-term or long-term)
    - **memory_id**: The unique identifier of the memory to delete
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
async def memory_operation_endpoint(
    request: MemoryOperationRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Perform a generic memory operation for an agent.

    - **agent_id**: The ID of the agent
    - **operation**: The memory operation to perform
    - **memory_type**: The type of memory (short-term or long-term)
    - **data**: Data required for the operation
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
