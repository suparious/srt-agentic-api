from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.agent import Agent

from uuid import UUID, uuid4
from app.core.models.agent import AgentConfig, AgentInfoResponse, AgentCreationRequest
from app.core.models.memory import MemoryConfig
from app.utils.logging import agent_logger
from app.core.memory import MemorySystem
from app.core.llm_provider import create_llm_provider



class AgentManager:
    """
    Manages the lifecycle and operations of agents in the system.
    """

    def __init__(self):
        """
        Initialize the AgentManager with an empty dictionary of agents.
        """
        self.agents: Dict[UUID, Agent] = {}

    async def create_agent(self, request: AgentCreationRequest) -> UUID:
        """
        Create a new agent with the given configuration and initial prompt.

        Args:
            name (str): The name of the agent.
            config (Dict[str, Any]): The configuration for the agent.
            memory_config (Dict[str, Any]): The memory configuration for the agent.
            initial_prompt (str): The initial prompt to send to the agent.

        Returns:
            UUID: The unique identifier of the created agent.

        Raises:
            HTTPException: If there's an error during agent creation.
        """
        try:
            agent_id = uuid4()

            memory_system = MemorySystem(agent_id, request.memory_config)
            llm_provider = create_llm_provider()

            agent = Agent(
                agent_id,
                request.agent_name,
                request.agent_config,
                memory_system,
                llm_provider
            )

            self.agents[agent_id] = agent

            # Process initial prompt
            await agent.process_message(request.initial_prompt)

            agent_logger.info(f"Agent {request.agent_name} (ID: {agent_id}) created successfully")
            return agent_id
        except Exception as e:
            agent_logger.error(f"Error creating Agent {request.agent_name}: {str(e)}")
            raise ValueError(f"Failed to create agent: {str(e)}")

    async def get_agent_info(self, agent_id: UUID) -> Optional[AgentInfoResponse]:
        """
        Retrieve information about a specific agent.

        Args:
            agent_id (UUID): The unique identifier of the agent.

        Returns:
            Optional[AgentInfoResponse]: The agent information if found, None otherwise.
        """
        agent = self.agents.get(agent_id)
        if not agent:
            agent_logger.warning(f"No agent found with id: {agent_id}")
            return None

        return AgentInfoResponse(
            agent_id=agent.id,
            name=agent.name,
            config=agent.config,
            memory_config=agent.memory.config,
            conversation_history_length=len(agent.conversation_history),
        )

    async def update_agent(self, agent_id: UUID, update_data: Dict[str, Any]) -> bool:
        """
        Update an existing agent's configuration.

        Args:
            agent_id (UUID): The unique identifier of the agent to update.
            update_data (Dict[str, Any]): The data to update the agent with.

        Returns:
            bool: True if the agent was successfully updated, False otherwise.
        """
        agent = self.agents.get(agent_id)
        if not agent:
            agent_logger.warning(f"No agent found with id: {agent_id} for update")
            return False

        try:
            if "config" in update_data:
                agent.config = AgentConfig(**update_data["config"])
            if "memory_config" in update_data:
                agent.memory.config = MemoryConfig(**update_data["memory_config"])
            agent_logger.info(
                f"Agent {agent.name} (ID: {agent_id}) updated successfully"
            )
            return True
        except Exception as e:
            agent_logger.error(
                f"Error updating Agent {agent.name} (ID: {agent_id}): {str(e)}"
            )
            return False

    async def delete_agent(self, agent_id: UUID) -> bool:
        """
        Delete an agent from the system.

        Args:
            agent_id (UUID): The unique identifier of the agent to delete.

        Returns:
            bool: True if the agent was successfully deleted, False otherwise.
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            agent_logger.info(f"Agent (ID: {agent_id}) deleted successfully")
            return True
        agent_logger.warning(f"No agent found with id: {agent_id} for deletion")
        return False

    async def list_agents(self) -> List[AgentInfoResponse]:
        """
        List all agents in the system.

        Returns:
            List[AgentInfoResponse]: A list of information about all agents.
        """
        return [
            AgentInfoResponse(
                agent_id=agent.id,
                name=agent.name,
                config=agent.config,
                memory_config=agent.memory.config,
                conversation_history_length=len(agent.conversation_history),
            )
            for agent in self.agents.values()
        ]

    async def get_agent_memory_config(self, agent_id: UUID) -> MemoryConfig:
        """
        Get the memory configuration of a specific agent.

        Args:
            agent_id (UUID): The unique identifier of the agent.

        Returns:
            MemoryConfig: The memory configuration of the agent.

        Raises:
            ValueError: If the agent is not found.
        """
        agent = self.agents.get(agent_id)
        if not agent:
            agent_logger.error(f"No agent found with id: {agent_id}")
            raise ValueError(f"No agent found with id: {agent_id}")
        return agent.memory.config

    async def process_message(
        self, agent_id: UUID, message: str
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process a message for a specific agent.

        Args:
            agent_id (UUID): The unique identifier of the agent.
            message (str): The message to process.

        Returns:
            Tuple[str, List[Dict[str, Any]]]: The processed message and any function calls.

        Raises:
            ValueError: If the agent is not found.
        """
        agent = self.agents.get(agent_id)
        if not agent:
            agent_logger.error(f"No agent found with id: {agent_id}")
            raise ValueError(f"No agent found with id: {agent_id}")
        return await agent.process_message(message)

    async def add_function_to_agent(
        self, agent_id: UUID, function: Dict[str, Any]
    ) -> bool:
        """
        Add a function to a specific agent.

        Args:
            agent_id (UUID): The unique identifier of the agent.
            function (Dict[str, Any]): The function definition to add.

        Returns:
            bool: True if the function was successfully added, False otherwise.

        Raises:
            ValueError: If the agent is not found.
        """
        agent = self.agents.get(agent_id)
        if not agent:
            agent_logger.error(f"No agent found with id: {agent_id}")
            raise ValueError(f"No agent found with id: {agent_id}")

        try:
            from app.api.models.function import FunctionDefinition

            function_def = FunctionDefinition(**function)
            agent.add_function(function_def)
            agent_logger.info(
                f"Function {function_def.name} added to Agent {agent.name} (ID: {agent_id})"
            )
            return True
        except Exception as e:
            agent_logger.error(
                f"Error adding function to Agent {agent.name} (ID: {agent_id}): {str(e)}"
            )
            return False

    async def remove_function_from_agent(
        self, agent_id: UUID, function_name: str
    ) -> bool:
        """
        Remove a function from a specific agent.

        Args:
            agent_id (UUID): The unique identifier of the agent.
            function_name (str): The name of the function to remove.

        Returns:
            bool: True if the function was successfully removed, False otherwise.

        Raises:
            ValueError: If the agent is not found.
        """
        agent = self.agents.get(agent_id)
        if not agent:
            agent_logger.error(f"No agent found with id: {agent_id}")
            raise ValueError(f"No agent found with id: {agent_id}")

        agent.remove_function(function_name)
        agent_logger.info(
            f"Function {function_name} removed from Agent {agent.name} (ID: {agent_id})"
        )
        return True


# Global instance of AgentManager
agent_manager = AgentManager()

# Import FunctionManager and set agent_manager
from app.core.function_manager import function_manager
function_manager.set_agent_manager(agent_manager)
