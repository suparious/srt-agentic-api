from fastapi import APIRouter, HTTPException, Depends
from app.api.models.memory import MemoryDeleteRequest, MemoryDeleteResponse
from app.utils.auth import get_api_key
from app.utils.logging import memory_logger
from .utils import get_memory_system

router = APIRouter()

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
        memory_system = await get_memory_system(request.agent_id)
        await memory_system.delete(request.memory_type, request.memory_id)
        memory_logger.info(f"Memory deleted successfully for agent: {request.agent_id}")
        return MemoryDeleteResponse(
            agent_id=request.agent_id,
            message="Memory deleted successfully"
        )
    except Exception as e:
        memory_logger.error(f"Error deleting memory for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
