import pytest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from chart_genius_mcp.server import ChartGeniusServer
from chart_genius_mcp.config import ChartGeniusConfig


@pytest.mark.asyncio
async def test_cache_stats_when_disabled():
    cfg = ChartGeniusConfig()
    cfg.cache_enabled = False
    srv = ChartGeniusServer(cfg)
    res = await srv._manage_cache("stats")
    assert res["success"] is False


@pytest.mark.asyncio
async def test_cache_clear_and_optimize_when_enabled():
    cfg = ChartGeniusConfig()
    cfg.cache_enabled = True
    cfg.cache_type = "memory"
    srv = ChartGeniusServer(cfg)
    res_stats = await srv._manage_cache("stats")
    assert res_stats["success"] is True

    res_clear = await srv._manage_cache("clear")
    assert res_clear["success"] is True

    res_opt = await srv._manage_cache("optimize")
    assert res_opt["success"] is True 