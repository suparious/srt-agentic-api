from fastapi import APIRouter, HTTPException, Depends
from app.api.models.agent import AgentMemoryRequest, AgentMemoryResponse, MemoryOperation
from app.core.memory import add_to_memory, retrieve_from_memory, search_memory
from app.utils.auth import get_api_key

router = APIRouter()


@router.post("/memory", response_model=AgentMemoryResponse)
async def memory_operation_endpoint(request: AgentMemoryRequest, api_key: str = Depends(get_api_key)):
    try:
        if request.operation == MemoryOperation.ADD:
            result = await add_to_memory(request.agent_id, request.data)
        elif request.operation == MemoryOperation.RETRIEVE:
            result = await retrieve_from_memory(request.agent_id, request.query)
        elif request.operation == MemoryOperation.SEARCH:
            result = await search_memory(request.agent_id, request.query)
        else:
            raise ValueError("Invalid memory operation")

        return AgentMemoryResponse(agent_id=request.agent_id, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))