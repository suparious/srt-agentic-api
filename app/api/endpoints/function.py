from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List
from app.api.models.function import (
    FunctionExecutionRequest,
    FunctionExecutionResponse,
    AvailableFunctionsRequest,
    AvailableFunctionsResponse,
    FunctionDefinition,
    FunctionRegistrationRequest,
    FunctionRegistrationResponse,
    FunctionUpdateRequest,
    FunctionUpdateResponse,
    FunctionAssignmentRequest,
    FunctionAssignmentResponse
)
from app.core.agent_manager import AgentManager
from app.utils.auth import get_api_key
from app.utils.logging import function_logger

router = APIRouter()

def get_agent_manager():
    return AgentManager()

@router.post("/execute", response_model=FunctionExecutionResponse, summary="Execute a function")
async def execute_function_endpoint(
    request: FunctionExecutionRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key)
):
    """
    Execute a function for a specific agent.

    - **agent_id**: The ID of the agent requesting the function execution
    - **function_name**: The name of the function to execute
    - **parameters**: The parameters to pass to the function
    """
    try:
        function_logger.info(f"Executing function {request.function_name} for agent: {request.agent_id}")
        agent = agent_manager.agents.get(request.agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {request.agent_id}")
        result = await agent.execute_function(request.function_name, request.parameters)
        function_logger.info(f"Function {request.function_name} executed successfully for agent: {request.agent_id}")
        return FunctionExecutionResponse(
            agent_id=request.agent_id,
            function_name=request.function_name,
            result=result
        )
    except ValueError as ve:
        function_logger.error(f"Value error in function execution: {str(ve)}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error executing function {request.function_name} for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while executing the function")

@router.get("/available", response_model=AvailableFunctionsResponse, summary="Get available functions")
async def get_available_functions_endpoint(
    request: AvailableFunctionsRequest = Depends(),
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key)
):
    """
    Retrieve available functions for a specific agent.

    - **agent_id**: The ID of the agent to retrieve available functions for
    """
    try:
        function_logger.info(f"Retrieving available functions for agent: {request.agent_id}")
        agent = agent_manager.agents.get(request.agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {request.agent_id}")
        functions = agent.get_available_functions()
        function_logger.info(f"Successfully retrieved available functions for agent: {request.agent_id}")
        return AvailableFunctionsResponse(
            agent_id=request.agent_id,
            functions=functions
        )
    except ValueError as ve:
        function_logger.error(f"Value error in retrieving available functions: {str(ve)}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error retrieving available functions for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving available functions")

@router.post("/register", response_model=FunctionRegistrationResponse, status_code=201, summary="Register a new function")
async def register_function_endpoint(
    request: FunctionRegistrationRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key)
):
    """
    Register a new function for use by agents.

    - **function**: The function definition to register
    """
    try:
        function_logger.info(f"Registering new function: {request.function.name}")
        function_id = str(UUID.uuid4())  # Generate a new UUID for the function
        for agent in agent_manager.agents.values():
            agent.add_function(request.function)
        function_logger.info(f"Successfully registered function: {function_id}")
        return FunctionRegistrationResponse(
            function_id=function_id,
            message="Function registered successfully"
        )
    except ValueError as ve:
        function_logger.error(f"Value error in function registration: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error registering function: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while registering the function")

@router.put("/update", response_model=FunctionUpdateResponse, summary="Update an existing function")
async def update_function_endpoint(
    request: FunctionUpdateRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key)
):
    """
    Update an existing function definition.

    - **function_id**: The unique identifier of the function to update
    - **updated_function**: The updated function definition
    """
    try:
        function_logger.info(f"Updating function: {request.function_id}")
        for agent in agent_manager.agents.values():
            if request.updated_function.name in agent.available_functions:
                agent.available_functions[request.updated_function.name] = request.updated_function
        function_logger.info(f"Successfully updated function: {request.function_id}")
        return FunctionUpdateResponse(
            function_id=request.function_id,
            message="Function updated successfully"
        )
    except ValueError as ve:
        function_logger.error(f"Value error in function update: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error updating function: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the function")

@router.post("/assign", response_model=FunctionAssignmentResponse, summary="Assign a function to an agent")
async def assign_function_endpoint(
    request: FunctionAssignmentRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key)
):
    """
    Assign a function to a specific agent.

    - **agent_id**: The ID of the agent to assign the function to
    - **function_id**: The ID of the function to assign
    """
    try:
        function_logger.info(f"Assigning function {request.function_id} to agent: {request.agent_id}")
        agent = agent_manager.agents.get(request.agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {request.agent_id}")
        function = next((f for f in agent.available_functions.values() if str(f.id) == request.function_id), None)
        if not function:
            raise ValueError(f"Function not found: {request.function_id}")
        agent.add_function(function)
        function_logger.info(f"Successfully assigned function {request.function_id} to agent: {request.agent_id}")
        return FunctionAssignmentResponse(
            agent_id=request.agent_id,
            function_id=request.function_id,
            message="Function assigned successfully"
        )
    except ValueError as ve:
        function_logger.error(f"Value error in function assignment: {str(ve)}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error assigning function: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while assigning the function")

@router.delete("/remove", response_model=FunctionAssignmentResponse, summary="Remove a function from an agent")
async def remove_function_endpoint(
    agent_id: UUID,
    function_id: str,
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key)
):
    """
    Remove a function from a specific agent.

    - **agent_id**: The ID of the agent to remove the function from
    - **function_id**: The ID of the function to remove
    """
    try:
        function_logger.info(f"Removing function {function_id} from agent: {agent_id}")
        agent = agent_manager.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        function_name = next((name for name, func in agent.available_functions.items() if str(func.id) == function_id), None)
        if not function_name:
            raise ValueError(f"Function not found: {function_id}")
        agent.remove_function(function_name)
        function_logger.info(f"Successfully removed function {function_id} from agent: {agent_id}")
        return FunctionAssignmentResponse(
            agent_id=agent_id,
            function_id=function_id,
            message="Function removed successfully"
        )
    except ValueError as ve:
        function_logger.error(f"Value error in function removal: {str(ve)}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error removing function: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while removing the function")
