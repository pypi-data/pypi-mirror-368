import os
import pytest
import pytest_asyncio
import pandas as pd

from chart_genius_mcp.server import ChartGeniusServer


@pytest_asyncio.fixture
async def server():
    srv = ChartGeniusServer()
    return srv


@pytest.mark.asyncio
async def test_generate_bar_chart_with_group_plotly(server: ChartGeniusServer):
    data = {
        "rows": [
            {"month": "Jan", "sales": 100, "region": "NA"},
            {"month": "Jan", "sales": 120, "region": "EU"},
            {"month": "Feb", "sales": 130, "region": "NA"},
        ]
    }
    out = await server._call_tool_handler(  # type: ignore[attr-defined]
        "generate_bar_chart",
        {
            "data": data,
            "x": "month",
            "y": "sales",
            "group": "region",
            "engine": "plotly",
            "format": "json",
        },
    )
    body = out[0].text
    assert "success" in body


@pytest.mark.asyncio
async def test_generate_line_chart_seaborn_mapping(server: ChartGeniusServer):
    data = {
        "rows": [
            {"x": 0, "y": 1, "series": "A"},
            {"x": 1, "y": 3, "series": "A"},
            {"x": 0, "y": 2, "series": "B"},
        ]
    }
    out = await server._call_tool_handler(  # type: ignore[attr-defined]
        "generate_line_chart",
        {
            "data": data,
            "x": "x",
            "y": "y",
            "group": "series",
            "engine": "seaborn",
            "format": "png",
        },
    )
    body = out[0].text
    assert "image/png" in body or "payload" in body


@pytest.mark.asyncio
async def test_generate_scatter_chart_matplotlib_mapping(server: ChartGeniusServer):
    data = {
        "rows": [
            {"x": 0, "y": 1, "g": "A"},
            {"x": 1, "y": 3, "g": "B"},
            {"x": 2, "y": 2, "g": "A"},
        ]
    }
    out = await server._call_tool_handler(  # type: ignore[attr-defined]
        "generate_scatter_chart",
        {
            "data": data,
            "x": "x",
            "y": "y",
            "color": "g",
            "engine": "matplotlib",
            "format": "png",
        },
    )
    body = out[0].text
    assert "image/png" in body or "payload" in body


@pytest.mark.asyncio
async def test_generate_pie_heatmap_sankey_plotly(server: ChartGeniusServer):
    # Pie
    pie_data = {"rows": [{"k": "A", "v": 10}, {"k": "B", "v": 5}]}
    out1 = await server._call_tool_handler(  # type: ignore[attr-defined]
        "generate_pie_chart",
        {"data": pie_data, "names": "k", "values": "v", "engine": "plotly", "format": "json"},
    )
    assert "success" in out1[0].text

    # Heatmap (simple grid-like data)
    heat_data = {"rows": [{"x": 0, "y": 0, "value": 1}, {"x": 1, "y": 0, "value": 2}]}
    out2 = await server._call_tool_handler(  # type: ignore[attr-defined]
        "generate_heatmap_chart",
        {"data": heat_data, "x": "x", "y": "y", "value": "value", "engine": "plotly", "format": "json"},
    )
    assert "success" in out2[0].text

    # Sankey
    sankey_data = {
        "rows": [
            {"source": "A", "target": "B", "value": 5},
            {"source": "B", "target": "C", "value": 3},
        ]
    }
    out3 = await server._call_tool_handler(  # type: ignore[attr-defined]
        "generate_sankey_chart",
        {"data": sankey_data, "source": "source", "target": "target", "value": "value", "engine": "plotly", "format": "json"},
    )
    assert "success" in out3[0].text


@pytest.mark.asyncio
async def test_generate_chart_auto_basic(server: ChartGeniusServer):
    data = {"rows": [{"month": "Jan", "sales": 100}, {"month": "Feb", "sales": 120}]}
    out = await server._call_tool_handler(  # type: ignore[attr-defined]
        "generate_chart_auto",
        {"data": data, "user_text": "show trend over time", "engine": "plotly", "format": "json"},
    )
    assert "success" in out[0].text 


@pytest.mark.asyncio
async def test_heatmap_treemap_sunburst_choropleth_mappings(server: ChartGeniusServer):
    # Heatmap with explicit x,y,value pivot
    heat_rows = [
        {"city": "SF", "day": "Mon", "temp": 60},
        {"city": "SF", "day": "Tue", "temp": 62},
        {"city": "NY", "day": "Mon", "temp": 50},
    ]
    out_h = await server._call_tool_handler(  # type: ignore[attr-defined]
        "generate_heatmap_chart",
        {"data": {"rows": heat_rows}, "x": "day", "y": "city", "value": "temp", "engine": "plotly", "format": "json"},
    )
    assert "success" in out_h[0].text

    # Treemap with path + value
    tree_rows = [
        {"continent": "Americas", "country": "US", "pop": 300},
        {"continent": "Americas", "country": "CA", "pop": 35},
    ]
    out_t = await server._call_tool_handler(  # type: ignore[attr-defined]
        "generate_treemap_chart",
        {"data": {"rows": tree_rows}, "path": ["continent", "country"], "value": "pop", "engine": "plotly", "format": "json"},
    )
    assert "success" in out_t[0].text

    # Sunburst with path + value
    out_s = await server._call_tool_handler(  # type: ignore[attr-defined]
        "generate_sunburst_chart",
        {"data": {"rows": tree_rows}, "path": ["continent", "country"], "value": "pop", "engine": "plotly", "format": "json"},
    )
    assert "success" in out_s[0].text

    # Choropleth with location + value
    chor_rows = [
        {"location": "USA", "value": 100},
        {"location": "CAN", "value": 50},
    ]
    out_c = await server._call_tool_handler(  # type: ignore[attr-defined]
        "generate_choropleth_chart",
        {"data": {"rows": chor_rows}, "location": "location", "value": "value", "engine": "plotly", "format": "json"},
    )
    assert "success" in out_c[0].text 