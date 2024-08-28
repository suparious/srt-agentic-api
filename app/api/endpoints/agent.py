from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List
from app.api.models.agent import (
    AgentCreationRequest,
    AgentCreationResponse,
    AgentInfoResponse,
    AgentUpdateRequest,
    AgentUpdateResponse,
)
from app.api.models.function import FunctionDefinition
from app.core.agent_manager import AgentManager
from app.utils.auth import get_api_key
from app.utils.logging import agent_logger
from app.dependencies import get_agent_manager, get_function_manager

router = APIRouter()


@router.post("/create", response_model=AgentCreationResponse, status_code=201)
async def create_agent_endpoint(
    request: AgentCreationRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key),
):
    """
    Create a new agent.

    - **agent_name**: The name of the agent
    - **agent_config**: Configuration for the agent's language model(s)
    - **memory_config**: Configuration for the agent's memory systems
    - **initial_prompt**: The initial prompt to send to the agent upon creation
    """
    try:
        agent_id = await agent_manager.create_agent(request)
        return AgentCreationResponse(
            agent_id=agent_id, message="Agent created successfully"
        )
    except ValueError as ve:
        agent_logger.error(f"ValueError in agent creation: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        agent_logger.error(f"Failed to create agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@router.get("/{agent_id}", response_model=AgentInfoResponse)
async def get_agent_info_endpoint(
    agent_id: UUID,
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key),
):
    """
    Retrieve information about a specific agent.

    - **agent_id**: The unique identifier of the agent
    """
    agent_info = await agent_manager.get_agent_info(agent_id)
    if agent_info is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_info


@router.patch("/{agent_id}", response_model=AgentUpdateResponse)
async def update_agent_endpoint(
    agent_id: UUID,
    request: AgentUpdateRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key),
):
    """
    Update an existing agent.

    - **agent_id**: The unique identifier of the agent to update
    - **config**: Updated configuration for the agent's language model (optional)
    - **memory_config**: Updated configuration for the agent's memory systems (optional)
    """
    updated = await agent_manager.update_agent(
        agent_id=agent_id, update_data=request.dict(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentUpdateResponse(agent_id=agent_id, message="Agent updated successfully")


@router.delete("/{agent_id}", status_code=204)
async def delete_agent_endpoint(
    agent_id: UUID,
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key),
):
    """
    Delete an agent.

    - **agent_id**: The unique identifier of the agent to delete
    """
    deleted = await agent_manager.delete_agent(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.get("/", response_model=List[AgentInfoResponse])
async def list_agents_endpoint(
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key),
):
    """
    List all agents.
    """
    return await agent_manager.list_agents()


@router.post("/{agent_id}/functions", status_code=201)
async def add_function_to_agent_endpoint(
    agent_id: UUID,
    function: FunctionDefinition,
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key),
):
    """
    Add a function to an agent.

    - **agent_id**: The unique identifier of the agent
    - **function**: The function definition to add to the agent
    """
    try:
        success = await agent_manager.add_function_to_agent(agent_id, function.dict())
        if not success:
            raise HTTPException(
                status_code=404, detail="Agent not found or function addition failed"
            )
        return {"message": f"Function {function.name} added to agent successfully"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add function to agent: {str(e)}"
        )


@router.delete("/{agent_id}/functions/{function_name}", status_code=204)
async def remove_function_from_agent_endpoint(
    agent_id: UUID,
    function_name: str,
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key),
):
    """
    Remove a function from an agent.

    - **agent_id**: The unique identifier of the agent
    - **function_name**: The name of the function to remove from the agent
    """
    try:
        success = await agent_manager.remove_function_from_agent(
            agent_id, function_name
        )
        if not success:
            raise HTTPException(status_code=404, detail="Agent or function not found")
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to remove function from agent: {str(e)}"
        )
