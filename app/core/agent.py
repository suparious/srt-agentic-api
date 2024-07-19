from uuid import UUID
from typing import Dict, Any, Tuple, List
from app.api.models.agent import AgentConfig, MemoryConfig
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
            if function_name == "get_current_time":
                from datetime import datetime
                return str(datetime.now())
            else:
                raise ValueError(f"Unknown function: {function_name}")
        except Exception as e:
            agent_logger.error(
                f"Error executing function {function_name} for Agent {self.name} (ID: {self.id}): {str(e)}")
            raise

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


# Global dictionary to store active agents
agents: Dict[UUID, Agent] = {}


async def create_agent(agent_id: UUID, name: str, config: AgentConfig, memory_config: MemoryConfig,
                       initial_prompt: str) -> None:
    try:
        agent = Agent(agent_id, name, config, memory_config)
        agents[agent_id] = agent
        await agent.process_message(initial_prompt)
        agent_logger.info(f"Agent {name} (ID: {agent_id}) created successfully")
    except Exception as e:
        agent_logger.error(f"Error creating Agent {name} (ID: {agent_id}): {str(e)}")
        raise


async def process_message(agent_id: UUID, message: str) -> Tuple[str, List[Dict[str, Any]]]:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")
    return await agent.process_message(message)


async def execute_function(agent_id: UUID, function_name: str, parameters: Dict[str, Any]) -> Any:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")
    return await agent.execute_function(function_name, parameters)
