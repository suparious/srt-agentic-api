from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional
from uuid import UUID

class FunctionDefinition(BaseModel):
    """
    Represents the definition of a function that can be called by an agent.
    """
    name: str = Field(..., description="The name of the function", example="calculate_sum")
    description: str = Field(..., description="A brief description of what the function does", example="Calculates the sum of two numbers")
    parameters: Dict[str, Any] = Field(..., description="The parameters the function accepts", example={"a": {"type": "number"}, "b": {"type": "number"}})
    return_type: str = Field(..., description="The type of value the function returns", example="number")

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            "example": {
                "name": "calculate_sum",
                "description": "Calculates the sum of two numbers",
                "parameters": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "return_type": "number"
            }
        }
    )

class FunctionRegistrationRequest(BaseModel):
    """
    Represents a request to register a new function for use by agents.
    """
    function: FunctionDefinition = Field(..., description="The function to register")

    model_config = ConfigDict(extra='forbid')

class FunctionRegistrationResponse(BaseModel):
    """
    Represents the response after registering a new function.
    """
    function_id: str = Field(..., description="The unique identifier assigned to the registered function", example="func_01234567")
    message: str = Field(..., description="A message indicating the result of the registration", example="Function registered successfully")

    model_config = ConfigDict(extra='forbid')

class FunctionExecutionRequest(BaseModel):
    """
    Represents a request to execute a function by an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent requesting the function execution", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    function_name: str = Field(..., description="The name of the function to execute", example="calculate_sum")
    parameters: Dict[str, Any] = Field(..., description="The parameters to pass to the function", example={"a": 5, "b": 3})

    model_config = ConfigDict(extra='forbid')

class FunctionExecutionResponse(BaseModel):
    """
    Represents the response after executing a function.
    """
    agent_id: UUID = Field(..., description="The ID of the agent that requested the function execution", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    function_name: str = Field(..., description="The name of the function that was executed", example="calculate_sum")
    result: Any = Field(..., description="The result of the function execution", example=8)
    error: Optional[str] = Field(default=None, description="Any error message if the function execution failed")

    model_config = ConfigDict(extra='forbid')

class AvailableFunctionsRequest(BaseModel):
    """
    Represents a request to retrieve available functions for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to retrieve available functions for", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")

    model_config = ConfigDict(extra='forbid')

class AvailableFunctionsResponse(BaseModel):
    """
    Represents the response containing available functions for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    functions: List[FunctionDefinition] = Field(..., description="List of available functions for the agent")

    model_config = ConfigDict(extra='forbid')

class FunctionUpdateRequest(BaseModel):
    """
    Represents a request to update an existing function definition.
    """
    function_id: str = Field(..., description="The unique identifier of the function to update", example="func_01234567")
    updated_function: FunctionDefinition = Field(..., description="The updated function definition")

    model_config = ConfigDict(extra='forbid')

class FunctionUpdateResponse(BaseModel):
    """
    Represents the response after updating a function definition.
    """
    function_id: str = Field(..., description="The unique identifier of the updated function", example="func_01234567")
    message: str = Field(..., description="A message indicating the result of the update", example="Function updated successfully")

    model_config = ConfigDict(extra='forbid')

class FunctionAssignmentRequest(BaseModel):
    """
    Represents a request to assign a function to an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to assign the function to", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    function_id: str = Field(..., description="The ID of the function to assign", example="func_01234567")

    model_config = ConfigDict(extra='forbid')

class FunctionAssignmentResponse(BaseModel):
    """
    Represents the response after assigning or removing a function to/from an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    function_id: str = Field(..., description="The ID of the function", example="func_01234567")
    message: str = Field(..., description="A message indicating the result of the operation", example="Function assigned successfully")

    model_config = ConfigDict(extra='forbid')
