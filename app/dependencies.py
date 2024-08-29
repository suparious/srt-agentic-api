from typing import TYPE_CHECKING
from fastapi import Depends

if TYPE_CHECKING:
    from app.core.agent_manager import AgentManager
from app.core.function_manager import function_manager

def get_agent_manager():
    return AgentManager()

def get_function_manager():
    return function_manager
