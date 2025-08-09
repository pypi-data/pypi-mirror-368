import os
import json
import asyncio
import pytest

from chart_genius_mcp.server import ChartGeniusServer


@pytest.mark.performance
@pytest.mark.asyncio
async def test_latency_p50_p90_smoke():
    server = ChartGeniusServer()
    # Simple smoke across a couple tools; small iterations to keep CI fast
    combos = [
        (
            "generate_bar_chart",
            {"data": {"rows": [{"x": "A", "y": 1}, {"x": "B", "y": 2}]}, "x": "x", "y": "y", "engine": "plotly", "format": "json"},
        ),
        (
            "generate_scatter_chart",
            {"data": {"rows": [{"x": 0, "y": 1}, {"x": 1, "y": 2}]}, "x": "x", "y": "y", "engine": "matplotlib", "format": "png"},
        ),
    ]
    results = {}
    for name, args in combos:
        latencies = []
        for _ in range(5):
            start = asyncio.get_running_loop().time()
            _ = await server._call_tool_handler(name, args)  # type: ignore[attr-defined]
            end = asyncio.get_running_loop().time()
            latencies.append((end - start) * 1000.0)
        latencies.sort()
        p50 = latencies[len(latencies)//2]
        p90 = latencies[int(0.9 * (len(latencies)-1))]
        results[name] = {"p50_ms": p50, "p90_ms": p90}
    # Basic sanity: p90 >= p50 and not absurd (e.g., < 10s)
    for r in results.values():
        assert r["p50_ms"] <= r["p90_ms"]
        assert r["p90_ms"] < 10000 