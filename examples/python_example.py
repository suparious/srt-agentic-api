import aiohttp
import asyncio
import json

API_BASE_URL = "http://localhost:8000"
API_KEY = "your_api_key_here"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

async def create_agent():
    async with aiohttp.ClientSession() as session:
        data = {
            "agent_name": "PythonTestAgent",
            "agent_config": {
                "llm_provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 150,
                "memory_config": {
                    "use_long_term_memory": True,
                    "use_redis_cache": True
                }
            },
            "memory_config": {
                "use_long_term_memory": True,
                "use_redis_cache": True
            },
            "initial_prompt": "You are a helpful assistant."
        }
        async with session.post(f"{API_BASE_URL}/agent/create", headers=headers, json=data) as response:
            result = await response.json()
            return result["agent_id"]

async def send_message(agent_id, content):
    async with aiohttp.ClientSession() as session:
        data = {
            "agent_id": agent_id,
            "content": content
        }
        async with session.post(f"{API_BASE_URL}/message/send", headers=headers, json=data) as response:
            return await response.json()

async def get_agent_info(agent_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/agent/{agent_id}", headers=headers) as response:
            return await response.json()

async def main():
    # Create an agent
    agent_id = await create_agent()
    print(f"Created agent with ID: {agent_id}")

    # Get agent information
    agent_info = await get_agent_info(agent_id)
    print(f"Agent info: {json.dumps(agent_info, indent=2)}")

    # Send a message to the agent
    message_response = await send_message(agent_id, "Hello, what can you help me with today?")
    print(f"Agent response: {message_response['response']}")

if __name__ == "__main__":
    asyncio.run(main())
