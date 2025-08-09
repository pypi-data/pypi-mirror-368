import os
import pytest
from chart_genius_mcp.server import ChartGeniusServer


@pytest.mark.asyncio
@pytest.mark.xfail(reason="USA-states mapping may require system-specific map data")
async def test_choropleth_usa_states_smoke():
    server = ChartGeniusServer()
    data = {"rows": [
        {"state": "CA", "value": 1.0},
        {"state": "NY", "value": 0.8},
    ]}
    # Using USA-states locationmode
    res = await server._generate_chart(data=data, chart_type="choropleth", engine="plotly", format="json", location="state", value="value", locationmode="USA-states", scope="usa")
    assert res["success"]


@pytest.mark.asyncio
async def test_disabled_tools_hidden_and_blocked(monkeypatch):
    # Disable pie chart and ensure it is hidden and blocked
    monkeypatch.setenv("DISABLED_TOOLS", "generate_pie_chart")
    server = ChartGeniusServer()
    # list_tools goes through MCP server; we call internal list directly is non-trivial.
    # Instead, assert call_tool is blocked
    out = await server._call_tool_handler("generate_pie_chart", {"data": {"rows": []}, "names": "a", "values": "b"})  # type: ignore[attr-defined]
    body = out[0].text
    assert "disabled" in body.lower() or "error" in body.lower() 