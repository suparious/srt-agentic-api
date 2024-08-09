from fastapi import APIRouter, HTTPException, Depends
from app.api.models.memory import MemoryRetrieveRequest, MemoryRetrieveResponse
from app.utils.auth import get_api_key
from app.utils.logging import memory_logger
from .utils import get_memory_system

router = APIRouter()


@router.get(
    "/retrieve",
    response_model=MemoryRetrieveResponse,
    summary="Retrieve a memory entry",
)
async def retrieve_memory_endpoint(
    request: MemoryRetrieveRequest = Depends(), api_key: str = Depends(get_api_key)
):
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
        memory_system = await get_memory_system(request.agent_id)
        memory = await memory_system.retrieve(request.memory_type, request.memory_id)
        if memory is None:
            raise HTTPException(status_code=404, detail="Memory not found")
        memory_logger.info(
            f"Memory retrieved successfully for agent: {request.agent_id}"
        )
        return MemoryRetrieveResponse(agent_id=request.agent_id, memory=memory)
    except HTTPException:
        raise
    except Exception as e:
        memory_logger.error(
            f"Error retrieving memory for agent {request.agent_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))
