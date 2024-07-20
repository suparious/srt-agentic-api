# tests/test_core/test_agent.py
import pytest
from unittest.mock import Mock, patch
from app.core.agent import Agent  # Import your Agent class

@pytest.fixture
def mock_memory():
    return Mock()

@pytest.fixture
def mock_llm_provider():
    return Mock()

def test_agent_initialization(mock_memory, mock_llm_provider):
    agent = Agent(memory=mock_memory, llm_provider=mock_llm_provider)
    assert agent.memory == mock_memory
    assert agent.llm_provider == mock_llm_provider

# Add more tests for Agent methods