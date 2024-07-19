from fastapi import APIRouter, HTTPException, Depends
from app.api.models.agent import AgentFunctionRequest, AgentFunctionResponse
from app.core.agent import execute_function
from app.utils.auth import get_api_key

router = APIRouter()

@router.post("/function", response_model=AgentFunctionResponse)
async def execute_function_endpoint(request: AgentFunctionRequest, api_key: str = Depends(get_api_key)):
    try:
        result = await execute_function(request.agent_id, request.function_name, request.parameters)
        return AgentFunctionResponse(agent_id=request.agent_id, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))