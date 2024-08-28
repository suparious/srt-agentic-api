from fastapi import APIRouter, HTTPException, Depends
from app.api.models.memory import MemoryAddRequest, MemoryAddResponse
from app.utils.auth import get_api_key
from app.utils.logging import memory_logger
from app.utils import get_memory_system

router = APIRouter()


@router.post(
    "/add",
    response_model=MemoryAddResponse,
    status_code=201,
    summary="Add a memory entry",
)
async def add_memory_endpoint(
    request: MemoryAddRequest, api_key: str = Depends(get_api_key)
):
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
        memory_system = await get_memory_system(request.agent_id)
        memory_id = await memory_system.add(request.memory_type, request.entry)
        memory_logger.info(f"Memory added successfully for agent: {request.agent_id}")
        return MemoryAddResponse(
            agent_id=request.agent_id,
            memory_id=memory_id,
            message="Memory added successfully",
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        memory_logger.error(
            f"Error adding memory for agent {request.agent_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))
