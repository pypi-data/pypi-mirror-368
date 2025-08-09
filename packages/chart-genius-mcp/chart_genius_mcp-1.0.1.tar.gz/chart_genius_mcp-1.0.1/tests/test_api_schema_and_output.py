import os
import json
import pytest
import pandas as pd

from chart_genius_mcp.server import ChartGeniusServer


@pytest.mark.asyncio
async def test_generate_chart_output_normalization():
    server = ChartGeniusServer()
    data = {
        "columns": ["month", "sales"],
        "rows": [
            {"month": "Jan", "sales": 100},
            {"month": "Feb", "sales": 120},
        ],
    }
    res = await server._generate_chart(data=data, chart_type="bar", engine="plotly", format="json")
    assert res["success"] is True
    # Normalized fields
    assert res["format"] == res["metadata"]["format"]
    assert res["content_type"] in {"application/json", "text/html", "image/png", "image/svg+xml", "application/pdf"}
    assert "payload" in res
    # Back-compat
    assert "chart" in res and "metadata" in res


@pytest.mark.asyncio
async def test_call_tool_validation_errors_are_user_friendly():
    server = ChartGeniusServer()
    # Missing required 'rows'
    bad_args = {"data": {"columns": ["a", "b"]}, "chart_type": "line"}
    out = await server._call_tool_handler("generate_chart", bad_args)  # type: ignore[attr-defined]
    payload = json.loads(out[0].text)
    assert "error" in payload
    assert "rows" in payload["error"].lower()


@pytest.mark.asyncio
async def test_call_tool_rejects_invalid_enum_values():
    server = ChartGeniusServer()
    data = {"columns": ["x", "y"], "rows": [{"x": 0, "y": 1}]}
    bad_args = {"data": data, "engine": "unknown"}
    out = await server._call_tool_handler("generate_chart", bad_args)  # type: ignore[attr-defined]
    payload = json.loads(out[0].text)
    assert "error" in payload
    assert "engine" in payload["error"].lower()


@pytest.mark.asyncio
async def test_invalid_chart_type_raises():
    server = ChartGeniusServer()
    data = {"columns": ["x", "y"], "rows": [{"x": 0, "y": 1}]}
    out = await server._call_tool_handler("generate_chart", {"data": data, "chart_type": "not_a_type"})
    payload = json.loads(out[0].text)
    assert "error" in payload
    # Accept Pydantic literal error wording
    assert "chart_type" in payload["error"].lower() or "input should be" in payload["error"].lower()


@pytest.mark.asyncio
async def test_invalid_format_fallback_reports_actual_format():
    server = ChartGeniusServer()
    data = {"columns": ["x", "y"], "rows": [{"x": 0, "y": 1}]}
    # Ask seaborn for unsupported "html"; it should generate png internally and normalize format/content_type
    res = await server._generate_chart(data=data, chart_type="line", engine="seaborn", format="html")
    assert res["success"] is True
    assert res["format"] in {"png", "svg", "pdf"}
    assert res["content_type"] in {"image/png", "image/svg+xml", "application/pdf"}


@pytest.mark.asyncio
async def test_engine_success_paths_plotly_matplotlib_seaborn():
    server = ChartGeniusServer()
    data = {"columns": ["x", "y"], "rows": [{"x": 0, "y": 1}, {"x": 1, "y": 3}]}

    # Plotly JSON
    r1 = await server._generate_chart(data=data, chart_type="line", engine="plotly", format="json")
    assert r1["success"] and r1["format"] == "json" and r1["content_type"] == "application/json"

    # Matplotlib PNG
    r2 = await server._generate_chart(data=data, chart_type="line", engine="matplotlib", format="png")
    assert r2["success"] and r2["format"] == "png" and r2["content_type"] == "image/png" and isinstance(r2["payload"], str)

    # Seaborn PNG
    r3 = await server._generate_chart(data=data, chart_type="line", engine="seaborn", format="png")
    assert r3["success"] and r3["format"] == "png" and r3["content_type"] == "image/png" and isinstance(r3["payload"], str) 