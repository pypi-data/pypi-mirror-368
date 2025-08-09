import os
import json
import asyncio
import pytest
import pandas as pd

from chart_genius_mcp.server import ChartGeniusServer


@pytest.mark.asyncio
async def test_timeout_guardrail(monkeypatch):
    os.environ["CHART_TOOL_TIMEOUT_MS"] = "50"
    server = ChartGeniusServer()

    async def slow_generate_chart(**kwargs):
        await asyncio.sleep(0.2)
        return {"success": True}

    # Monkeypatch the internal method used after validation
    monkeypatch.setattr(server, "_generate_chart", slow_generate_chart)

    args = {"data": {"columns": ["x", "y"], "rows": [{"x": 0, "y": 1}]}}
    out = await server._call_tool_handler("generate_chart", args)  # type: ignore[attr-defined]
    body = json.loads(out[0].text)
    assert "error" in body  # timeout path should return error


@pytest.mark.asyncio
async def test_input_size_cap(monkeypatch):
    os.environ["CHART_MAX_ROWS"] = "3"
    server = ChartGeniusServer()

    data = {"columns": ["x"], "rows": [{"x": 0}, {"x": 1}, {"x": 2}, {"x": 3}]}
    out = await server._call_tool_handler("generate_chart", {"data": data})  # type: ignore[attr-defined]
    body = json.loads(out[0].text)
    assert "error" in body and "too large" in body["error"].lower()


@pytest.mark.asyncio
async def test_cache_key_version_and_ttl(monkeypatch):
    os.environ["CHART_CACHE_KEY_VERSION"] = "v9"
    os.environ["CHART_CACHE_TTL_DEFAULT"] = "1234"
    server = ChartGeniusServer()

    # Capture ttl passed to cache.set
    captured = {}

    async def fake_set(key, value, ttl: int):
        captured["key"] = key
        captured["ttl"] = ttl
        return True

    monkeypatch.setattr(server.cache, "set", fake_set, raising=True)  # type: ignore[attr-defined]

    data = {"columns": ["x", "y"], "rows": [{"x": 0, "y": 1}, {"x": 1, "y": 2}]}
    res = await server._generate_chart(data=data, chart_type="line", engine="plotly", format="json")
    assert res["success"]
    assert captured.get("key", "").startswith("v9:")
    assert captured.get("ttl") == 1234 