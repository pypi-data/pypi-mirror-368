import pytest
import pandas as pd
from chart_genius_mcp.server import ChartGeniusServer
from chart_genius_mcp.exceptions import ChartGenerationError


@pytest.mark.asyncio
async def test_heatmap_pivot_plotly_success():
    server = ChartGeniusServer()
    data = {
        "rows": [
            {"x": "Mon", "y": "Morning", "value": 2},
            {"x": "Tue", "y": "Morning", "value": 4},
            {"x": "Mon", "y": "Evening", "value": 3},
        ]
    }
    res = await server._generate_chart(data=data, chart_type="heatmap", engine="plotly", format="json", x="x", y="y", value="value")
    assert res["success"]
    assert res["format"] == "json"


@pytest.mark.asyncio
async def test_heatmap_pivot_matplotlib_success_png():
    server = ChartGeniusServer()
    data = {
        "rows": [
            {"x": "Mon", "y": "Morning", "value": 2},
            {"x": "Tue", "y": "Morning", "value": 4},
            {"x": "Mon", "y": "Evening", "value": 3},
        ]
    }
    res = await server._generate_chart(data=data, chart_type="heatmap", engine="matplotlib", format="png", x="x", y="y", value="value")
    assert res["success"]
    assert res["format"] == "png"
    assert isinstance(res["payload"], str) and len(res["payload"]) > 0


@pytest.mark.asyncio
async def test_heatmap_pivot_seaborn_success_png():
    server = ChartGeniusServer()
    data = {
        "rows": [
            {"x": "Mon", "y": "Morning", "value": 2},
            {"x": "Tue", "y": "Morning", "value": 4},
            {"x": "Mon", "y": "Evening", "value": 3},
        ]
    }
    res = await server._generate_chart(data=data, chart_type="heatmap", engine="seaborn", format="png", x="x", y="y", value="value")
    assert res["success"]
    assert res["format"] == "png"
    assert isinstance(res["payload"], str) and len(res["payload"]) > 0


@pytest.mark.asyncio
async def test_heatmap_pivot_invalid_mapping_error():
    server = ChartGeniusServer()
    data = {"rows": [{"a": 1, "b": 2}]}
    with pytest.raises(ChartGenerationError):
        await server._generate_chart(data=data, chart_type="heatmap", engine="plotly", format="json", x="x", y="y", value="value") 