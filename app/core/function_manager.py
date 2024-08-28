from uuid import UUID, uuid4
from typing import Dict, Any, List, Optional
from app.core.models import FunctionDefinition
from app.utils.logging import agent_logger

class FunctionManager:
    """
    Manages the registration, execution, and assignment of functions to agents in the system.
    """

    def __init__(self):
        """
        Initialize the FunctionManager with an empty dictionary of registered functions.
        """
        self.registered_functions: Dict[str, FunctionDefinition] = {}
        self.agent_manager = None

    def set_agent_manager(self, agent_manager):
        """
        Set the agent manager after initialization to avoid circular imports.
        """
        self.agent_manager = agent_manager

    async def register_function(self, function: FunctionDefinition) -> str:
        """
        Register a new function in the system.

        Args:
            function (FunctionDefinition): The function to register.

        Returns:
            str: The unique identifier assigned to the registered function.
        """
        function_id = str(uuid4())
        self.registered_functions[function_id] = function
        agent_logger.info(f"Function {function.name} registered with ID: {function_id}")
        return function_id

    async def update_function(
            self, function_id: str, updated_function: FunctionDefinition
    ) -> None:
        """
        Update an existing function in the system.

        Args:
            function_id (str): The unique identifier of the function to update.
            updated_function (FunctionDefinition): The updated function definition.

        Raises:
            ValueError: If the function is not found.
        """
        if function_id not in self.registered_functions:
            raise ValueError(f"No function found with id: {function_id}")

        self.registered_functions[function_id] = updated_function
        agent_logger.info(f"Function with ID: {function_id} updated successfully")

        if self.agent_manager:
            for agent in self.agent_manager.agents.values():
                if function_id in agent.available_function_ids:
                    agent.add_function(function_id)
                    agent_logger.info(
                        f"Updated function {updated_function.name} for Agent {agent.name} (ID: {agent.id})"
                    )

    async def assign_function_to_agent(self, agent_id: UUID, function_id: str) -> None:
        """
        Assign a function to a specific agent.

        Args:
            agent_id (UUID): The unique identifier of the agent.
            function_id (str): The unique identifier of the function to assign.

        Raises:
            ValueError: If the agent or function is not found.
        """
        if not self.agent_manager:
            raise RuntimeError("AgentManager not set")

        agent = self.agent_manager.agents.get(agent_id)
        if not agent:
            agent_logger.error(f"No agent found with id: {agent_id}")
            raise ValueError(f"No agent found with id: {agent_id}")

        if function_id not in self.registered_functions:
            agent_logger.error(f"No function found with id: {function_id}")
            raise ValueError(f"No function found with id: {function_id}")

        agent.add_function(function_id)
        agent_logger.info(
            f"Function {self.registered_functions[function_id].name} assigned to Agent {agent.name} (ID: {agent_id})"
        )

    async def remove_function_from_agent(
        self, agent_id: UUID, function_id: str
    ) -> None:
        """
        Remove a function from a specific agent.

        Args:
            agent_id (UUID): The unique identifier of the agent.
            function_id (str): The unique identifier of the function to remove.

        Raises:
            ValueError: If the agent or function is not found.
        """
        agent = self.agent_manager.agents.get(agent_id)
        if not agent:
            agent_logger.error(f"No agent found with id: {agent_id}")
            raise ValueError(f"No agent found with id: {agent_id}")

        if function_id not in self.registered_functions:
            agent_logger.error(f"No function found with id: {function_id}")
            raise ValueError(f"No function found with id: {function_id}")

        agent.remove_function(function_id)
        agent_logger.info(
            f"Function {self.registered_functions[function_id].name} removed from Agent {agent.name} (ID: {agent_id})"
        )

    async def get_function(self, function_id: str) -> Optional[FunctionDefinition]:
        return self.registered_functions.get(function_id)

    async def list_functions(self) -> List[FunctionDefinition]:
        return list(self.registered_functions.values())

    async def execute_function(
        self, agent_id: UUID, function_name: str, parameters: Dict[str, Any]
    ) -> Any:
        """
        Execute a function for a specific agent.

        Args:
            agent_id (UUID): The unique identifier of the agent.
            function_name (str): The name of the function to execute.
            parameters (Dict[str, Any]): The parameters to pass to the function.

        Returns:
            Any: The result of the function execution.

        Raises:
            ValueError: If the agent or function is not found.
        """
        agent = self.agent_manager.agents.get(agent_id)
        if not agent:
            agent_logger.error(f"No agent found with id: {agent_id}")
            raise ValueError(f"No agent found with id: {agent_id}")

        try:
            agent_logger.info(
                f"Executing function {function_name} for Agent {agent.name} (ID: {agent.id})"
            )
            get_function = agent.get_function_by_name(function_name)
            if not get_function:
                raise ValueError(f"Unknown function: {function_name}")

            func_impl = self.registered_functions[get_function.id].implementation

            result = await func_impl(**parameters)

            agent_logger.info(
                f"Function {function_name} executed successfully for Agent {agent.name} (ID: {agent.id})"
            )
            return result
        except Exception as e:
            agent_logger.error(
                f"Error executing function {function_name} for Agent {agent.name} (ID: {agent.id}): {str(e)}"
            )
            raise

    async def get_available_functions(self, agent_id: UUID) -> List[FunctionDefinition]:
        """
        Get the list of available functions for a specific agent.

        Args:
            agent_id (UUID): The unique identifier of the agent.

        Returns:
            List[FunctionDefinition]: A list of available function definitions for the agent.

        Raises:
            ValueError: If the agent is not found.
        """
        agent = self.agent_manager.agents.get(agent_id)
        if not agent:
            agent_logger.error(f"No agent found with id: {agent_id}")
            raise ValueError(f"No agent found with id: {agent_id}")

        return [
            self.registered_functions[func_id]
            for func_id in agent.available_function_ids
            if func_id in self.registered_functions
        ]

# Global instance of FunctionManager
function_manager = FunctionManager()
