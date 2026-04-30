import pytest
import json
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from app.services.agent_service import AgentService
from app.ai.schemas import AgentMessage, AgentToolCall, AgentResponse

@pytest.mark.asyncio
async def test_agent_service_iterative_loop():
    # Mock dependencies
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    
    with patch("app.services.agent_service.DentalAgent") as MockAgent:
        agent_instance = MockAgent.return_value
        
        # Sequence of responses: Tool call then Final response
        agent_instance.get_response = AsyncMock(side_effect=[
            AgentResponse(
                content="Checking services...",
                tool_calls=[
                    AgentToolCall(
                        id="call_1",
                        tool_name="get_clinic_services",
                        arguments={}
                    )
                ]
            ),
            AgentResponse(
                content="We offer cleaning and fillings. Which would you like?",
                tool_calls=[]
            )
        ])
        
        service = AgentService(mock_db, mock_redis)
        
        # Mock database execution for get_clinic_services
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        response = await service.handle_turn(
            history=[AgentMessage(role="user", content="What services do you have?")],
            session_id="test-session"
        )
        
        assert "cleaning and fillings" in response.content
        assert agent_instance.get_response.call_count == 2
        mock_db.execute.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])
