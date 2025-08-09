import os
import sys
import time
import pytest
import importlib.util

from chart_genius_mcp.server import ChartGeniusServer
from chart_genius_mcp.config import ChartGeniusConfig

redis_available = importlib.util.find_spec("redis") is not None


@pytest.mark.asyncio
@pytest.mark.skipif(not redis_available, reason="redis not installed")
async def test_redis_cache_e2e_cached_and_faster(monkeypatch):
    cfg = ChartGeniusConfig()
    cfg.cache_enabled = True
    cfg.cache_type = "redis"
    cfg.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    srv = ChartGeniusServer(cfg)

    data = {"columns": ["x", "y"], "rows": [{"x": i, "y": i} for i in range(1000)]}

    # Try a quick connect probe
    try:
        import redis.asyncio as redis
        client = redis.from_url(cfg.redis_url)
        await client.ping()
    except Exception:
        pytest.skip("redis server not reachable")

    t1 = time.time()
    r1 = await srv._generate_chart(data=data, chart_type="line", engine="plotly", format="json")
    d1 = (time.time() - t1) * 1000

    t2 = time.time()
    r2 = await srv._generate_chart(data=data, chart_type="line", engine="plotly", format="json")
    d2 = (time.time() - t2) * 1000

    assert r1["success"] and r2["success"]
    assert r2["metadata"].get("cached") is True
    assert d2 <= d1  # cached should not be slower 