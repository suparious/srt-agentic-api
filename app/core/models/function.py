from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional, Callable
from uuid import UUID, uuid4

class FunctionDefinition(BaseModel):
    """
    Represents the definition of a function that can be called by an agent.
    """

    id: UUID = Field(
        default_factory=uuid4, description="The unique identifier of the function"
    )
    name: str = Field(
        ..., description="The name of the function", example="calculate_sum"
    )
    description: str = Field(
        ...,
        description="A brief description of what the function does",
        example="Calculates the sum of two numbers",
    )
    parameters: Dict[str, Any] = Field(
        ...,
        description="The parameters the function accepts",
        example={"a": {"type": "number"}, "b": {"type": "number"}},
    )
    return_type: str = Field(
        ..., description="The type of value the function returns", example="number"
    )
    implementation: Optional[Callable] = Field(
        None, description="The actual implementation of the function"
    )

    model_config = ConfigDict(
        extra="forbid",
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "calculate_sum",
                "description": "Calculates the sum of two numbers",
                "parameters": {"a": {"type": "number"}, "b": {"type": "number"}},
                "return_type": "number",
            }
        },
    )

