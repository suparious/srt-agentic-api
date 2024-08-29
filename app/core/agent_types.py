from typing import Protocol, Dict, Any
from uuid import UUID

class AgentProtocol(Protocol):
    id: UUID
    name: str

    async def process_message(self, message: str) -> Dict[str, Any]:
        ...

    async def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Any:
        ...

# Add any other shared types or interfaces here