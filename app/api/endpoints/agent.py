from fastapi import APIRouter, HTTPException, Depends
from app.api.models.agent import AgentCreationRequest, AgentCreationResponse
from app.core.agent import create_agent
from app.utils.auth import get_api_key
from uuid import uuid4

router = APIRouter()

@router.post("/create", response_model=AgentCreationResponse)
async def create_agent_endpoint(request: AgentCreationRequest, api_key: str = Depends(get_api_key)):
    try:
        agent_id = uuid4()
        await create_agent(agent_id, request.agent_name, request.agent_config, request.memory_config, request.initial_prompt)
        return AgentCreationResponse(agent_id=agent_id, message="Agent created successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))