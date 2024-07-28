from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List
from app.api.models.agent import AgentCreationRequest, AgentCreationResponse, AgentInfoResponse, AgentUpdateRequest, AgentUpdateResponse
from app.core.agent import create_agent, get_agent_info, update_agent, delete_agent, list_agents
from app.utils.auth import get_api_key

router = APIRouter()

@router.post("/create", response_model=AgentCreationResponse, status_code=201)
async def create_agent_endpoint(request: AgentCreationRequest, api_key: str = Depends(get_api_key)):
    """
    Create a new agent.

    - **agent_name**: The name of the agent
    - **agent_config**: Configuration for the agent's language model(s)
    - **memory_config**: Configuration for the agent's memory systems
    - **initial_prompt**: The initial prompt to send to the agent upon creation
    """
    agent_id = await create_agent(
        name=request.agent_name,
        config=request.agent_config.dict(),
        memory_config=request.memory_config.dict(),
        initial_prompt=request.initial_prompt
    )
    return AgentCreationResponse(agent_id=agent_id, message="Agent created successfully")

@router.get("/{agent_id}", response_model=AgentInfoResponse)
async def get_agent_info_endpoint(agent_id: UUID, api_key: str = Depends(get_api_key)):
    """
    Retrieve information about a specific agent.

    - **agent_id**: The unique identifier of the agent
    """
    agent_info = await get_agent_info(agent_id=agent_id)
    if agent_info is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_info

@router.patch("/{agent_id}", response_model=AgentUpdateResponse)
async def update_agent_endpoint(agent_id: UUID, request: AgentUpdateRequest, api_key: str = Depends(get_api_key)):
    """
    Update an existing agent.

    - **agent_id**: The unique identifier of the agent to update
    - **config**: Updated configuration for the agent's language model (optional)
    - **memory_config**: Updated configuration for the agent's memory systems (optional)
    """
    updated = await update_agent(
        agent_id=agent_id,
        update_data=request.dict(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentUpdateResponse(agent_id=agent_id, message="Agent updated successfully")

@router.delete("/{agent_id}", status_code=204)
async def delete_agent_endpoint(agent_id: UUID, api_key: str = Depends(get_api_key)):
    """
    Delete an agent.

    - **agent_id**: The unique identifier of the agent to delete
    """
    deleted = await delete_agent(agent_id=agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")

@router.get("/", response_model=List[AgentInfoResponse])
async def list_agents_endpoint(api_key: str = Depends(get_api_key)):
    """
    List all agents.
    """
    return await list_agents()
