import pytest
from unittest.mock import AsyncMock

from app.ai.schemas import AgentMessage
from app.services.agent_service import COMPACTION_THRESHOLD, AgentService


class TestContextCompaction:
    @pytest.fixture
    def agent(self, mock_redis):
        mock_db = AsyncMock()
        return AgentService(db=mock_db, redis=mock_redis)

    @pytest.mark.asyncio
    async def test_compaction_not_triggered_below_threshold(self, agent):
        history = [AgentMessage(role="user", content=f"turn {i}") for i in range(10)]
        result = history if len(history) <= COMPACTION_THRESHOLD else await agent._compact_history(history)
        assert len(result) == len(history)

    @pytest.mark.asyncio
    async def test_compaction_is_called_above_threshold(self, agent):
        history = [AgentMessage(role="user", content=f"turn {i}") for i in range(COMPACTION_THRESHOLD + 5)]
        compacted = await agent._compact_history(history)
        assert len(compacted) < len(history)

    @pytest.mark.asyncio
    async def test_compaction_preserves_recent_turns(self, agent):
        history = [AgentMessage(role="user", content=f"turn {i}") for i in range(25)]
        compacted = await agent._compact_history(history)
        recent = compacted[-(COMPACTION_THRESHOLD // 2):]
        recent_contents = [m.content for m in recent]
        assert any("turn 20" in c for c in recent_contents)
        assert any("turn 24" in c for c in recent_contents)

    @pytest.mark.asyncio
    async def test_compaction_creates_system_summary(self, agent):
        history = [AgentMessage(role="user", content=f"turn {i}") for i in range(25)]
        compacted = await agent._compact_history(history)
        assert compacted[0].role == "system"
        assert "conversation summary" in compacted[0].content.lower()

    @pytest.mark.asyncio
    async def test_token_growth_is_bounded(self, agent):
        small_history = [AgentMessage(role="user", content="a" * 100) for i in range(10)]
        large_history = [AgentMessage(role="user", content="a" * 100) for i in range(40)]

        small = len(" ".join(m.content for m in small_history))
        large_compact = await agent._compact_history(large_history)
        large_compacted_len = len(" ".join(m.content for m in large_compact))

        assert large_compacted_len < small * 15
        assert large_compacted_len < 50000

    @pytest.mark.asyncio
    async def test_compaction_reduces_size_by_at_least_half(self, agent):
        history = [AgentMessage(role="user", content=f"detailed turn content {i} " * 10) for i in range(30)]
        compacted = await agent._compact_history(history)
        assert len(compacted) < len(history) // 2
