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
    FunctionUpdateResponse
)
from app.core.agent import execute_function, get_available_functions, register_function, update_function
from app.utils.auth import get_api_key
from app.utils.logging import function_logger

router = APIRouter()

@router.post("/execute", response_model=FunctionExecutionResponse, summary="Execute a function")
async def execute_function_endpoint(
    request: FunctionExecutionRequest,
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
        result = await execute_function(request.agent_id, request.function_name, request.parameters)
        function_logger.info(f"Function {request.function_name} executed successfully for agent: {request.agent_id}")
        return FunctionExecutionResponse(
            agent_id=request.agent_id,
            function_name=request.function_name,
            result=result
        )
    except ValueError as ve:
        function_logger.error(f"Value error in function execution: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error executing function {request.function_name} for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while executing the function")

@router.get("/available", response_model=AvailableFunctionsResponse, summary="Get available functions")
async def get_available_functions_endpoint(
    request: AvailableFunctionsRequest = Depends(),
    api_key: str = Depends(get_api_key)
):
    """
    Retrieve available functions for a specific agent.

    - **agent_id**: The ID of the agent to retrieve available functions for
    """
    try:
        function_logger.info(f"Retrieving available functions for agent: {request.agent_id}")
        functions = await get_available_functions(request.agent_id)
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

@router.post("/register", response_model=FunctionRegistrationResponse, summary="Register a new function")
async def register_function_endpoint(
    request: FunctionRegistrationRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Register a new function for use by agents.

    - **function**: The function definition to register
    """
    try:
        function_logger.info(f"Registering new function: {request.function.name}")
        function_id = await register_function(request.function)
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
    api_key: str = Depends(get_api_key)
):
    """
    Update an existing function definition.

    - **function_id**: The unique identifier of the function to update
    - **updated_function**: The updated function definition
    """
    try:
        function_logger.info(f"Updating function: {request.function_id}")
        await update_function(request.function_id, request.updated_function)
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
