import inspect
import asyncio
from uuid import UUID, uuid4
from typing import Dict, Any, Tuple, List, Optional
from app.api.models.agent import AgentConfig, MemoryConfig, AgentInfoResponse
from app.api.models.function import FunctionDefinition
from app.api.models.memory import MemoryType
from app.core.llm_provider import create_llm_provider
from app.core.memory import MemorySystem
from app.utils.logging import agent_logger
from fastapi import HTTPException

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

            relevant_context = await self.memory.retrieve_relevant(message)
            prompt = self._prepare_prompt(relevant_context)

            response = await self.llm_provider.generate(prompt, self.config.temperature, self.config.max_tokens)
            response_text, function_calls = self._parse_response(response)

            self.conversation_history.append({"role": "assistant", "content": response_text})
            await self.memory.add(MemoryType.SHORT_TERM, response_text, {"type": "assistant_response"})

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

            func_impl = registered_functions[get_function.id].implementation

            result = await func_impl(**parameters)

            agent_logger.info(f"Function {function_name} executed successfully for Agent {self.name} (ID: {self.id})")
            return result
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

# Facade functions for interacting with agents
async def create_agent(name: str, config: Dict[str, Any], memory_config: Dict[str, Any], initial_prompt: str) -> UUID:
    try:
        agent_id = uuid4()
        agent_config = AgentConfig(**config)
        mem_config = MemoryConfig(**memory_config)
        agent = Agent(agent_id, name, agent_config, mem_config)
        agents[agent_id] = agent
        await agent.process_message(initial_prompt)
        agent_logger.info(f"Agent {name} (ID: {agent_id}) created successfully")
        return agent_id
    except Exception as e:
        agent_logger.error(f"Error creating Agent {name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")

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

async def update_agent(agent_id: UUID, update_data: Dict[str, Any]) -> bool:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.warning(f"No agent found with id: {agent_id} for update")
        return False

    try:
        if 'config' in update_data:
            agent.config = AgentConfig(**update_data['config'])
        if 'memory_config' in update_data:
            agent.memory.config = MemoryConfig(**update_data['memory_config'])
        agent_logger.info(f"Agent {agent.name} (ID: {agent_id}) updated successfully")
        return True
    except Exception as e:
        agent_logger.error(f"Error updating Agent {agent.name} (ID: {agent_id}): {str(e)}")
        return False

async def delete_agent(agent_id: UUID) -> bool:
    if agent_id in agents:
        del agents[agent_id]
        agent_logger.info(f"Agent (ID: {agent_id}) deleted successfully")
        return True
    agent_logger.warning(f"No agent found with id: {agent_id} for deletion")
    return False

async def list_agents() -> List[AgentInfoResponse]:
    return [
        AgentInfoResponse(
            agent_id=agent.id,
            name=agent.name,
            config=agent.config,
            memory_config=agent.memory.config,
            conversation_history_length=len(agent.conversation_history)
        )
        for agent in agents.values()
    ]

async def get_agent_memory_config(agent_id: UUID) -> MemoryConfig:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")
    return agent.config.memory_config

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

async def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Any:
    try:
        agent_logger.info(f"Executing function {function_name} for Agent {self.name} (ID: {self.id})")
        get_function = self.get_function_by_name(function_name)
        if not get_function:
            raise ValueError(f"Unknown function: {function_name}")

        func_impl = registered_functions[get_function.id].implementation

        result = await func_impl(**parameters)  # Ensure this is awaited

        agent_logger.info(f"Function {function_name} executed successfully for Agent {self.name} (ID: {self.id})")
        return result
    except Exception as e:
        agent_logger.error(f"Error executing function {function_name} for Agent {self.name} (ID: {self.id}): {str(e)}")
        raise

def get_available_functions(self) -> List[FunctionDefinition]:
    return [registered_functions[func_id] for func_id in self.available_function_ids if func_id in registered_functions]

async def update_function(function_id: str, updated_function: FunctionDefinition) -> None:
    if function_id not in registered_functions:
        agent_logger.error(f"No function found with id: {function_id}")
        raise ValueError(f"No function found with id: {function_id}")

    registered_functions[function_id] = updated_function
    agent_logger.info(f"Function with ID: {function_id} updated successfully")

    for agent in agents.values():
        if function_id in agent.available_function_ids:
            agent.add_function(function_id)
            agent_logger.info(f"Updated function {updated_function.name} for Agent {agent.name} (ID: {agent.id})")

async def assign_function_to_agent(agent_id: UUID, function_id: str) -> None:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")

    if function_id not in registered_functions:
        agent_logger.error(f"No function found with id: {function_id}")
        raise ValueError(f"No function found with id: {function_id}")

    agent.add_function(function_id)
    agent_logger.info(f"Function {registered_functions[function_id].name} assigned to Agent {agent.name} (ID: {agent_id})")

async def remove_function_from_agent(agent_id: UUID, function_id: str) -> None:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")

    if function_id not in registered_functions:
        agent_logger.error(f"No function found with id: {function_id}")
        raise ValueError(f"No function found with id: {function_id}")

    agent.remove_function(function_id)
    agent_logger.info(f"Function {registered_functions[function_id].name} removed from Agent {agent.name} (ID: {agent_id})")
