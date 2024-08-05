from fastapi import APIRouter, HTTPException, Depends
from app.api.models.memory import MemoryOperationRequest, MemoryOperationResponse
from app.utils.auth import get_api_key
from app.utils.logging import memory_logger
from .utils import get_memory_system

router = APIRouter()

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
        memory_system = await get_memory_system(request.agent_id)
        result = await memory_system.perform_operation(request.operation, request.memory_type, request.data)
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
