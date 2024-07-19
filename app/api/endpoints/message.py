from fastapi import APIRouter, HTTPException, Depends
from app.api.models.agent import AgentMessageRequest, AgentMessageResponse
from app.core.agent import process_message
from app.utils.auth import get_api_key

router = APIRouter()

@router.post("/message", response_model=AgentMessageResponse)
async def send_message_endpoint(request: AgentMessageRequest, api_key: str = Depends(get_api_key)):
    try:
        response, function_calls = await process_message(request.agent_id, request.message)
        return AgentMessageResponse(agent_id=request.agent_id, response=response, function_calls=function_calls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))