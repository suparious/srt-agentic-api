from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List
from app.api.models.function import (
    FunctionExecutionRequest,
    FunctionExecutionResponse,
    AvailableFunctionsRequest,
    AvailableFunctionsResponse,
    FunctionDefinition
)
from app.core.agent import execute_function, get_available_functions
from app.utils.auth import get_api_key
from app.utils.logging import function_logger

router = APIRouter()

@router.post("/execute", response_model=FunctionExecutionResponse)
async def execute_function_endpoint(
    request: FunctionExecutionRequest,
    api_key: str = Depends(get_api_key)
):
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

@router.get("/available", response_model=AvailableFunctionsResponse)
async def get_available_functions_endpoint(
    request: AvailableFunctionsRequest = Depends(),
    api_key: str = Depends(get_api_key)
):
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

# Note: If we want to add endpoints for registering new functions or updating existing ones,
# we would add them here. This would require implementing corresponding functions in app/core/agent.py.

# @router.post("/register", response_model=FunctionRegistrationResponse)
# async def register_function_endpoint(request: FunctionRegistrationRequest, api_key: str = Depends(get_api_key)):
#     # Implementation for registering a new function
#     pass

# @router.put("/update", response_model=FunctionUpdateResponse)
# async def update_function_endpoint(request: FunctionUpdateRequest, api_key: str = Depends(get_api_key)):
#     # Implementation for updating an existing function
#     pass
