import os
import sys
import pytest
import importlib.util

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from chart_genius_mcp.server import ChartGeniusServer
from chart_genius_mcp.config import ChartGeniusConfig


redis_available = importlib.util.find_spec("redis") is not None


@pytest.mark.asyncio
@pytest.mark.skipif(not redis_available, reason="redis not installed")
async def test_redis_cache_stats(monkeypatch):
    cfg = ChartGeniusConfig()
    cfg.cache_enabled = True
    cfg.cache_type = "redis"
    cfg.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    server = ChartGeniusServer(cfg)
    stats = await server._manage_cache("stats")
    assert stats["success"] is True
    assert "cache_stats" in stats 