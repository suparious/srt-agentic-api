const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'your_api_key_here';

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY
};

async function createAgent() {
  const data = {
    agent_name: 'JavaScriptTestAgent',
    agent_config: {
      llm_provider: 'openai',
      model_name: 'gpt-3.5-turbo',
      temperature: 0.7,
      max_tokens: 150,
      memory_config: {
        use_long_term_memory: true,
        use_redis_cache: true
      }
    },
    memory_config: {
      use_long_term_memory: true,
      use_redis_cache: true
    },
    initial_prompt: 'You are a helpful assistant.'
  };

  try {
    const response = await axios.post(`${API_BASE_URL}/agent/create`, data, { headers });
    return response.data.agent_id;
  } catch (error) {
    console.error('Error creating agent:', error.response ? error.response.data : error.message);
    throw error;
  }
}

async function sendMessage(agentId, content) {
  const data = {
    agent_id: agentId,
    content: content
  };

  try {
    const response = await axios.post(`${API_BASE_URL}/message/send`, data, { headers });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error.response ? error.response.data : error.message);
    throw error;
  }
}

async function getAgentInfo(agentId) {
  try {
    const response = await axios.get(`${API_BASE_URL}/agent/${agentId}`, { headers });
    return response.data;
  } catch (error) {
    console.error('Error getting agent info:', error.response ? error.response.data : error.message);
    throw error;
  }
}

async function main() {
  try {
    // Create an agent
    const agentId = await createAgent();
    console.log(`Created agent with ID: ${agentId}`);

    // Get agent information
    const agentInfo = await getAgentInfo(agentId);
    console.log('Agent info:', JSON.stringify(agentInfo, null, 2));

    // Send a message to the agent
    const messageResponse = await sendMessage(agentId, 'Hello, what can you help me with today?');
    console.log('Agent response:', messageResponse.response);
  } catch (error) {
    console.error('An error occurred:', error);
  }
}

main();
