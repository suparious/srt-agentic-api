from uuid import UUID
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime
from app.core.models.agent import AgentConfig
from app.core.models.function import FunctionDefinition
from app.core.llm_provider import LLMProvider
from app.utils.logging import agent_logger
from app.core.function_manager import function_manager

# Lazy import for MemorySystem
def get_memory_system():
    from app.core.memory.memory_system import MemorySystem
    return MemorySystem

class Agent:
    """
    Represents an AI agent capable of processing messages, managing memory, and executing functions.
    """

    def __init__(
        self,
        agent_id: UUID,
        name: str,
        config: AgentConfig,
        llm_provider: LLMProvider
    ):
        """
        Initialize a new Agent instance.

        Args:
            agent_id (UUID): The unique identifier for the agent.
            name (str): The name of the agent.
            config (AgentConfig): The configuration for the agent's language model.
            memory_config (MemoryConfig): The configuration for the agent's memory system.
        """
        self.id = agent_id
        self.name = name
        self.config = config
        self.llm_provider = llm_provider
        self.memory = get_memory_system()(agent_id, config.memory_config)
        self.conversation_history = []
        self.available_function_ids: List[str] = []
        agent_logger.info(f"Agent {self.name} (ID: {self.id}) initialized")

    async def process_message(self, message: str) -> str:
        """
        Process a message and generate a response.

        Args:
            message (str): The input message to process.

        Returns:
            Tuple[str, List[Dict[str, Any]]]: A tuple containing the response text and a list of function calls.

        Raises:
            Exception: If there's an error processing the message.
        """
        try:
            agent_logger.info(f"Processing message for Agent {self.name} (ID: {self.id})")
            self.conversation_history.append({"role": "user", "content": message})

            relevant_context = await self.memory.retrieve_relevant(message)
            prompt = self._prepare_prompt(relevant_context)

            response = await self.llm_provider.generate(
                prompt, self.config.temperature, self.config.max_tokens
            )

            self.conversation_history.append({"role": "assistant", "content": response})

            await self.memory.add(
                "SHORT_TERM",
                {
                    "content": response,
                    "metadata": {"type": "assistant_response"},
                    "context": {"context_type": "message", "timestamp": datetime.now().isoformat()}
                }
            )

            agent_logger.info(f"Message processed successfully for Agent {self.name} (ID: {self.id})")
            return response
        except Exception as e:
            agent_logger.error(f"Error processing message for Agent {self.name} (ID: {self.id}): {str(e)}")
            raise

    async def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a function with the given name and parameters.

        Args:
            function_name (str): The name of the function to execute.
            parameters (Dict[str, Any]): The parameters to pass to the function.

        Returns:
            Any: The result of the function execution.

        Raises:
            ValueError: If the function is not found.
            Exception: If there's an error executing the function.
        """
        return await function_manager.execute_function(self.id, function_name, parameters)

    async def get_available_functions(self) -> List[FunctionDefinition]:
        """
        Get the list of available functions for this agent.

        Returns:
            List[FunctionDefinition]: A list of available function definitions.
        """
        return await function_manager.get_available_functions(self.id)

    def add_function(self, function_id: str) -> None:
        """
        Add a function to the agent's available functions.

        Args:
            function (FunctionDefinition): The function to add.
        """
        if function_id not in self.available_function_ids:
            self.available_function_ids.append(function_id)
            agent_logger.info(f"Function {function_id} added to Agent {self.name} (ID: {self.id})")
        else:
            agent_logger.warning(
                f"Function {function_id} already available for Agent {self.name} (ID: {self.id})"
            )

    def remove_function(self, function_id: str) -> None:
        """
        Remove a function from the agent's available functions.

        Args:
            function_name (str): The name of the function to remove.
        """
        if function_id in self.available_function_ids:
            self.available_function_ids.remove(function_id)
            agent_logger.info(f"Function {function_id} removed from Agent {self.name} (ID: {self.id})")
        else:
            agent_logger.warning(
                f"Attempted to remove non-existent function {function_id} from Agent {self.name} (ID: {self.id})"
            )

    async def get_function_by_name(self, function_name: str) -> Optional[FunctionDefinition]:
        """
        Get a function definition by its name.

        Args:
            function_name (str): The name of the function to retrieve.

        Returns:
            Optional[FunctionDefinition]: The function definition if found, None otherwise.
        """
        for func_id in self.available_function_ids:
            func = await function_manager.get_function(func_id)
            if func and func.name == function_name:
                return func
        return None

    def _prepare_prompt(self, context: List[Dict[str, Any]]) -> str:
        """
        Prepare the prompt for the language model based on the context and conversation history.

        Args:
            context (List[Dict[str, Any]]): The relevant context for the prompt.

        Returns:
            str: The prepared prompt.
        """
        context_str = "\n".join([f"Context: {item['content']}" for item in context])
        history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history[-5:]])
        return f"{context_str}\n\nConversation History:\n{history}\n\nAssistant:"

    def _parse_response(self, response: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Parse the response from the language model to extract function calls.

        Args:
            response (str): The raw response from the language model.

        Returns:
            Tuple[str, List[Dict[str, Any]]]: A tuple containing the cleaned response text and a list of function calls.
        """
        function_calls = []
        if "FUNCTION CALL:" in response:
            parts = response.split("FUNCTION CALL:")
            response = parts[0].strip()
            for call in parts[1:]:
                try:
                    function_name, args = call.split("(", 1)
                    args = args.rsplit(")", 1)[0]
                    function_calls.append(
                        {
                            "name": function_name.strip(),
                            "arguments": eval(f"dict({args})"),
                        }
                    )
                except Exception as e:
                    agent_logger.warning(
                        f"Error parsing function call for Agent {self.name} (ID: {self.id}): {str(e)}"
                    )
        return response, function_calls
