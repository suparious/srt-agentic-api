from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from app.api.models.agent import AgentCreationRequest, AgentCreationResponse, AgentInfoResponse
from app.core.agent import create_agent, get_agent_info
from app.utils.auth import get_api_key
from app.utils.logging import agent_logger

router = APIRouter()

@router.post("/create", response_model=AgentCreationResponse)
async def create_agent_endpoint(request: AgentCreationRequest, api_key: str = Depends(get_api_key)):
    try:
        agent_logger.info(f"Received request to create agent: {request.agent_name}")
        agent_id = await create_agent(request.agent_name, request.agent_config, request.memory_config, request.initial_prompt)
        agent_logger.info(f"Agent created successfully: {agent_id}")
        return AgentCreationResponse(agent_id=agent_id, message="Agent created successfully")
    except Exception as e:
        agent_logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")

@router.get("/{agent_id}", response_model=AgentInfoResponse)
async def get_agent_info_endpoint(agent_id: UUID, api_key: str = Depends(get_api_key)):
    try:
        agent_logger.info(f"Received request to get info for agent: {agent_id}")
        agent_info = await get_agent_info(agent_id)
        if agent_info is None:
            agent_logger.warning(f"Agent not found: {agent_id}")
            raise HTTPException(status_code=404, detail="Agent not found")
        agent_logger.info(f"Successfully retrieved info for agent: {agent_id}")
        return agent_info
    except HTTPException:
        raise
    except Exception as e:
        agent_logger.error(f"Error retrieving agent info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving agent info: {str(e)}")

# Additional endpoints can be added here for updating agent configurations, 
# listing all agents, or deleting agents as needed.
