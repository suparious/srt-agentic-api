from fastapi import APIRouter, HTTPException, Depends
from app.api.models.agent import AgentMessageRequest, AgentMessageResponse
from app.core.agent_manager import AgentManager
from app.utils.auth import get_api_key
from app.utils.logging import agent_logger

router = APIRouter()


def get_agent_manager():
    return AgentManager()


@router.post("/send", response_model=AgentMessageResponse)
async def send_message_to_agent(
    request: AgentMessageRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    api_key: str = Depends(get_api_key)
):
    try:
        agent_logger.info(f"Received message for agent: {request.agent_id}")
        response, function_calls = await agent_manager.process_message(
            request.agent_id, request.message
        )
        agent_logger.info(
            f"Successfully processed message for agent: {request.agent_id}"
        )
        return AgentMessageResponse(
            agent_id=request.agent_id, response=response, function_calls=function_calls
        )
    except ValueError as ve:
        agent_logger.error(f"Agent not found: {request.agent_id}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        agent_logger.error(
            f"Error processing message for agent {request.agent_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="An error occurred while processing the message"
        )


# Note: If we want to add an endpoint for retrieving message history, we would add it here.
# This would require implementing a function in app/core/agent.py to retrieve the conversation history.

# @router.get("/{agent_id}/history", response_model=List[MessageHistoryItem])
# async def get_message_history(agent_id: UUID, limit: int = 10, api_key: str = Depends(get_api_key)):
#     # Implementation for retrieving message history
#     pass
