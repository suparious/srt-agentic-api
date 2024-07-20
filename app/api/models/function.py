from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from uuid import UUID

class FunctionDefinition(BaseModel):
    """
    Represents the definition of a function that can be called by an agent.
    """
    name: str = Field(..., description="The name of the function")
    description: str = Field(..., description="A brief description of what the function does")
    parameters: Dict[str, Any] = Field(..., description="The parameters the function accepts")
    return_type: str = Field(..., description="The type of value the function returns")

class FunctionRegistrationRequest(BaseModel):
    """
    Represents a request to register a new function for use by agents.
    """
    function: FunctionDefinition = Field(..., description="The function to register")

class FunctionRegistrationResponse(BaseModel):
    """
    Represents the response after registering a new function.
    """
    function_id: str = Field(..., description="The unique identifier assigned to the registered function")
    message: str = Field(..., description="A message indicating the result of the registration")

class FunctionExecutionRequest(BaseModel):
    """
    Represents a request to execute a function by an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent requesting the function execution")
    function_name: str = Field(..., description="The name of the function to execute")
    parameters: Dict[str, Any] = Field(..., description="The parameters to pass to the function")

class FunctionExecutionResponse(BaseModel):
    """
    Represents the response after executing a function.
    """
    agent_id: UUID = Field(..., description="The ID of the agent that requested the function execution")
    function_name: str = Field(..., description="The name of the function that was executed")
    result: Any = Field(..., description="The result of the function execution")
    error: Optional[str] = Field(default=None, description="Any error message if the function execution failed")

class AvailableFunctionsRequest(BaseModel):
    """
    Represents a request to retrieve available functions for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to retrieve available functions for")

class AvailableFunctionsResponse(BaseModel):
    """
    Represents the response containing available functions for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    functions: List[FunctionDefinition] = Field(..., description="List of available functions for the agent")

class FunctionUpdateRequest(BaseModel):
    """
    Represents a request to update an existing function definition.
    """
    function_id: str = Field(..., description="The unique identifier of the function to update")
    updated_function: FunctionDefinition = Field(..., description="The updated function definition")

class FunctionUpdateResponse(BaseModel):
    """
    Represents the response after updating a function definition.
    """
    function_id: str = Field(..., description="The unique identifier of the updated function")
    message: str = Field(..., description="A message indicating the result of the update")
