import os
import sys
import json
import pytest
from contextlib import AsyncExitStack

pytestmark = pytest.mark.integration


async def start_stdio_session(env_overrides=None):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    import sys as _sys
    env = os.environ.copy()
    env["PYTHONPATH"] = "/Users/inwookbaek/Desktop/chart-genius-mcp/src"
    env["CHART_CACHE_ENABLED"] = env.get("CHART_CACHE_ENABLED", "false")
    if env_overrides:
        env.update(env_overrides)
    stack = AsyncExitStack()
    params = StdioServerParameters(
        command=_sys.executable,
        args=["-m", "chart_genius_mcp"],
        env=env,
    )
    stdio_transport = await stack.enter_async_context(stdio_client(params))
    read_stream, write_stream = stdio_transport
    session = await stack.enter_async_context(ClientSession(read_stream, write_stream))
    await session.initialize()
    return stack, session


@pytest.mark.asyncio
async def test_detect_optimal_chart_and_analyze_and_visualize():
    stack, session = await start_stdio_session()
    try:
        data = {"columns": ["month", "sales"], "rows": [{"month": "Jan", "sales": 1}, {"month": "Feb", "sales": 2}]}
        det = await session.call_tool("detect_optimal_chart", {"data": data, "analysis_goal": "trends"})
        rec = json.loads(det.content[0].text)
        assert rec["success"] is True
        assert "recommendation" in rec

        av = await session.call_tool(
            "analyze_and_visualize",
            {"data": data, "question": "What is the trend?", "context": "business"},
        )
        av_obj = json.loads(av.content[0].text)
        assert av_obj["success"] is True
        assert "chart" in av_obj
        assert av_obj["analysis"]["recommended_chart"]
    finally:
        await stack.aclose()


@pytest.mark.asyncio
async def test_create_dashboard_and_export_chart():
    stack, session = await start_stdio_session()
    try:
        data = {"columns": ["x", "y"], "rows": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]}
        charts = [
            {"data": data, "chart_type": "line", "engine": "plotly"},
            {"data": data, "chart_type": "bar", "engine": "matplotlib"},
        ]
        dash = await session.call_tool("create_dashboard", {"charts": charts, "layout": "grid", "theme": "modern"})
        dash_obj = json.loads(dash.content[0].text)
        assert dash_obj["success"] is True
        assert len(dash_obj["dashboard"]["charts"]) == 2

        # Export mock (server returns simple export response)
        first_chart = dash_obj["dashboard"]["charts"][0]
        exp = await session.call_tool("export_chart", {"chart_data": first_chart, "format": "png"})
        exp_obj = json.loads(exp.content[0].text)
        assert exp_obj["success"] is True
        assert exp_obj["format"] == "png"
    finally:
        await stack.aclose()


@pytest.mark.asyncio
async def test_generate_chart_batch_parallel_vs_sequential():
    stack, session = await start_stdio_session()
    try:
        datasets = [
            {"columns": ["c", "v"], "rows": [{"c": "A", "v": 1}, {"c": "B", "v": 2}]},
            {"columns": ["c", "v"], "rows": [{"c": "A", "v": 3}, {"c": "B", "v": 4}]},
        ]
        chart_configs = [
            {"chart_type": "bar", "engine": "plotly"},
            {"chart_type": "bar", "engine": "plotly"},
        ]
        res_par = await session.call_tool(
            "generate_chart_batch",
            {"datasets": datasets, "chart_configs": chart_configs, "parallel": True},
        )
        par_obj = json.loads(res_par.content[0].text)
        assert par_obj["success"] is True
        assert par_obj["batch_stats"]["total_charts"] == 2
        assert par_obj["batch_stats"]["parallel_execution"] is True

        res_seq = await session.call_tool(
            "generate_chart_batch",
            {"datasets": datasets, "chart_configs": chart_configs, "parallel": False},
        )
        seq_obj = json.loads(res_seq.content[0].text)
        assert seq_obj["success"] is True
        assert seq_obj["batch_stats"]["parallel_execution"] is False

        # Include an invalid dataset to ensure error aggregation
        bad_datasets = datasets + [{"columns": ["x"], "rows": []}]  # empty should trigger error
        bad_cfgs = chart_configs + [{"chart_type": "bar", "engine": "plotly"}]
        res_bad = await session.call_tool(
            "generate_chart_batch",
            {"datasets": bad_datasets, "chart_configs": bad_cfgs, "parallel": True},
        )
        bad_obj = json.loads(res_bad.content[0].text)
        assert bad_obj["batch_stats"]["failed_charts"] >= 1
    finally:
        await stack.aclose()


@pytest.mark.asyncio
async def test_get_performance_stats_and_manage_cache_via_mcp():
    stack, session = await start_stdio_session({"CHART_CACHE_ENABLED": "true"})
    try:
        stats = await session.call_tool("get_performance_stats", {"include_history": False})
        stats_obj = json.loads(stats.content[0].text)
        assert stats_obj["success"] is True
        assert "performance_stats" in stats_obj

        cache_stats = await session.call_tool("manage_cache", {"action": "stats"})
        cache_obj = json.loads(cache_stats.content[0].text)
        assert cache_obj["success"] is True or cache_obj.get("message") == "Cache not enabled"

        # Invalid schema input for generate_chart: missing 'data'
        invalid = await session.call_tool("generate_chart", {"engine": "plotly"})
        inv_text = invalid.content[0].text
        assert "Input validation error" in inv_text
    finally:
        await stack.aclose() 