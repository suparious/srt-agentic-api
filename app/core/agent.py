import inspect
from uuid import UUID, uuid4
from typing import Dict, Any, Tuple, List, Optional
from app.api.models.agent import AgentConfig, MemoryConfig, AgentInfoResponse
from app.api.models.function import FunctionDefinition
from app.core.llm_provider import create_llm_provider
from app.core.memory import MemorySystem
from app.utils.logging import agent_logger


class Agent:
    def __init__(self, agent_id: UUID, name: str, config: AgentConfig, memory_config: MemoryConfig):
        self.id = agent_id
        self.name = name
        self.config = config
        self.llm_provider = create_llm_provider({
            'provider_type': config.llm_provider,
            'model_name': config.model_name
        })
        self.memory = MemorySystem(agent_id, memory_config)
        self.conversation_history = []
        self.available_function_ids: List[str] = []
        agent_logger.info(f"Agent {self.name} (ID: {self.id}) initialized with {config.llm_provider} provider")

    async def process_message(self, message: str) -> Tuple[str, List[Dict[str, Any]]]:
        try:
            agent_logger.info(f"Processing message for Agent {self.name} (ID: {self.id})")
            self.conversation_history.append({"role": "user", "content": message})

            context = await self.memory.retrieve_relevant(message)
            prompt = self._prepare_prompt(context)

            response = await self.llm_provider.generate(prompt, self.config.temperature, self.config.max_tokens)
            response_text, function_calls = self._parse_response(response)

            self.conversation_history.append({"role": "assistant", "content": response_text})
            await self.memory.add(response_text, {"type": "assistant_response"})

            agent_logger.info(f"Message processed successfully for Agent {self.name} (ID: {self.id})")
            return response_text, function_calls
        except Exception as e:
            agent_logger.error(f"Error processing message for Agent {self.name} (ID: {self.id}): {str(e)}")
            raise

    async def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Any:
        try:
            agent_logger.info(f"Executing function {function_name} for Agent {self.name} (ID: {self.id})")
            get_function = self.get_function_by_name(function_name)
            if not get_function:
                raise ValueError(f"Unknown function: {function_name}")

            # Get the actual function implementation
            func_impl = registered_functions[function.id].implementation

            # Validate parameters
            sig = inspect.signature(func_impl)
            bound_args = sig.bind(**parameters)
            bound_args.apply_defaults()

            # Execute the function
            result = func_impl(**bound_args.arguments)

            agent_logger.info(f"Function {function_name} executed successfully for Agent {self.name} (ID: {self.id})")
            return result
        except ValueError as ve:
            agent_logger.error(f"Value error executing function {function_name} for Agent {self.name} (ID: {self.id}): {str(ve)}")
            raise
        except TypeError as te:
            agent_logger.error(f"Type error executing function {function_name} for Agent {self.name} (ID: {self.id}): {str(te)}")
            raise ValueError(f"Invalid parameters for function {function_name}: {str(te)}")
        except Exception as e:
            agent_logger.error(f"Error executing function {function_name} for Agent {self.name} (ID: {self.id}): {str(e)}")
            raise

    def get_available_functions(self) -> List[FunctionDefinition]:
        return [registered_functions[func_id] for func_id in self.available_function_ids if func_id in registered_functions]

    def add_function(self, function_id: str):
        if function_id not in registered_functions:
            raise ValueError(f"Function with ID {function_id} is not registered")
        if function_id not in self.available_function_ids:
            self.available_function_ids.append(function_id)
            agent_logger.info(f"Function {registered_functions[function_id].name} added for Agent {self.name} (ID: {self.id})")
        else:
            agent_logger.warning(f"Function {registered_functions[function_id].name} already available for Agent {self.name} (ID: {self.id})")

    def remove_function(self, function_id: str):
        if function_id in self.available_function_ids:
            self.available_function_ids.remove(function_id)
            agent_logger.info(f"Function {registered_functions[function_id].name} removed from Agent {self.name} (ID: {self.id})")
        else:
            agent_logger.warning(f"Attempted to remove non-existent function {function_id} from Agent {self.name} (ID: {self.id})")

    def get_function_by_name(self, function_name: str) -> Optional[FunctionDefinition]:
        for func_id in self.available_function_ids:
            if func_id in registered_functions and registered_functions[func_id].name == function_name:
                return registered_functions[func_id]
        return None

    def _prepare_prompt(self, context: List[Dict[str, Any]]) -> str:
        context_str = "\n".join([f"Context: {item['content']}" for item in context])
        history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history[-5:]])
        return f"{context_str}\n\nConversation History:\n{history}\n\nAssistant:"

    def _parse_response(self, response: str) -> Tuple[str, List[Dict[str, Any]]]:
        function_calls = []
        if "FUNCTION CALL:" in response:
            parts = response.split("FUNCTION CALL:")
            response = parts[0].strip()
            for call in parts[1:]:
                try:
                    function_name, args = call.split("(", 1)
                    args = args.rsplit(")", 1)[0]
                    function_calls.append({
                        "name": function_name.strip(),
                        "arguments": eval(f"dict({args})")
                    })
                except Exception as e:
                    agent_logger.warning(f"Error parsing function call for Agent {self.name} (ID: {self.id}): {str(e)}")
        return response, function_calls


# Global dictionaries
agents: Dict[UUID, Agent] = {}
registered_functions: Dict[str, FunctionDefinition] = {}

async def create_agent(name: str, config: AgentConfig, memory_config: MemoryConfig, initial_prompt: str) -> UUID:
    try:
        agent_id = uuid4()
        agent = Agent(agent_id, name, config, memory_config)
        agents[agent_id] = agent
        await agent.process_message(initial_prompt)
        agent_logger.info(f"Agent {name} (ID: {agent_id}) created successfully")
        return agent_id
    except Exception as e:
        agent_logger.error(f"Error creating Agent {name}: {str(e)}")
        raise


async def get_agent_info(agent_id: UUID) -> Optional[AgentInfoResponse]:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.warning(f"No agent found with id: {agent_id}")
        return None

    return AgentInfoResponse(
        agent_id=agent.id,
        name=agent.name,
        config=agent.config,
        memory_config=agent.memory.config,
        conversation_history_length=len(agent.conversation_history)
    )


async def process_message(agent_id: UUID, message: str) -> Tuple[str, List[Dict[str, Any]]]:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")
    return await agent.process_message(message)

async def register_function(function: FunctionDefinition) -> str:
    function_id = str(uuid4())
    registered_functions[function_id] = function
    agent_logger.info(f"Function {function.name} registered with ID: {function_id}")
    return function_id

async def execute_function(agent_id: UUID, function_name: str, parameters: Dict[str, Any]) -> Any:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")
    return await agent.execute_function(function_name, parameters)


async def get_available_functions(agent_id: UUID) -> List[FunctionDefinition]:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")
    return agent.get_available_functions()


async def register_function(function: FunctionDefinition) -> str:
    function_id = str(uuid4())
    registered_functions[function_id] = function
    agent_logger.info(f"Function {function.name} registered with ID: {function_id}")
    return function_id


async def update_function(function_id: str, updated_function: FunctionDefinition) -> None:
    if function_id not in registered_functions:
        agent_logger.error(f"No function found with id: {function_id}")
        raise ValueError(f"No function found with id: {function_id}")

    registered_functions[function_id] = updated_function
    agent_logger.info(f"Function with ID: {function_id} updated successfully")

    # Update function for all agents that have it
    for agent in agents.values():
        if updated_function.name in agent.available_functions:
            agent.add_function(updated_function)
            agent_logger.info(f"Updated function {updated_function.name} for Agent {agent.name} (ID: {agent.id})")
