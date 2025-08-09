import asyncio
import os
import sys
import json
import pytest

from contextlib import AsyncExitStack

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_mcp_stdio_list_tools_and_generate_chart():
    # Use absolute project root
    env = os.environ.copy()
    env["PYTHONPATH"] = "/Users/inwookbaek/Desktop/chart-genius-mcp/src"
    # Ensure clean, fast behavior for test
    env["CHART_CACHE_ENABLED"] = "false"
    env["CHART_AI_FEATURES"] = "false"

    # Import client pieces lazily to avoid dependency if mcp not present
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except Exception:  # pragma: no cover
        pytest.skip("mcp client not available")

    async with AsyncExitStack() as stack:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "chart_genius_mcp"],
            env=env,
        )
        stdio_transport = await stack.enter_async_context(stdio_client(params))
        read_stream, write_stream = stdio_transport
        session = await stack.enter_async_context(ClientSession(read_stream, write_stream))

        await session.initialize()
        tools_response = await session.list_tools()
        tool_names = {t.name for t in tools_response.tools}
        assert "generate_chart" in tool_names

        # Call a simple chart generation
        data = {
            "columns": ["month", "sales"],
            "rows": [
                {"month": "Jan", "sales": 100},
                {"month": "Feb", "sales": 120},
            ],
        }
        result = await session.call_tool(
            "generate_chart",
            {
                "data": data,
                "chart_type": "bar",
                "engine": "plotly",
                "format": "json",
                "optimize_large_data": False,
            },
        )
        # result.content is a list of Content; first is text JSON
        payload = result.content[0].text
        obj = json.loads(payload)
        assert obj["success"] is True
        assert obj["metadata"]["engine"] == "plotly" 