import pytest

from chart_genius_mcp.server import ChartGeniusServer
from chart_genius_mcp.config import ChartGeniusConfig
from chart_genius_mcp.exceptions import ChartGenerationError


@pytest.mark.asyncio
async def test_empty_dataset_raises():
    cfg = ChartGeniusConfig()
    srv = ChartGeniusServer(cfg)
    data = {"columns": ["x"], "rows": []}
    with pytest.raises(ChartGenerationError):
        await srv._generate_chart(data=data, chart_type="line", engine="plotly")


@pytest.mark.asyncio
async def test_invalid_chart_type_engine_format():
    cfg = ChartGeniusConfig()
    srv = ChartGeniusServer(cfg)
    data = {"columns": ["x", "y"], "rows": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]}

    # invalid chart_type
    with pytest.raises(ChartGenerationError):
        await srv._generate_chart(data=data, chart_type="not_a_chart", engine="plotly")

    # invalid engine
    with pytest.raises(ChartGenerationError):
        await srv._generate_chart(data=data, chart_type="line", engine="no_engine")

    # invalid format for matplotlib currently falls back to png in engine; ensure result returns format
    res = await srv._generate_chart(data=data, chart_type="line", engine="matplotlib", format="xyz")
    assert res["success"] is True
    assert res["metadata"]["format"] in ("png", "svg", "pdf")


@pytest.mark.asyncio
async def test_theme_config_smoke():
    cfg = ChartGeniusConfig()
    srv = ChartGeniusServer(cfg)
    data = {"columns": ["m", "v"], "rows": [{"m": "A", "v": 1}, {"m": "B", "v": 2}]}
    for theme in ("corporate", "dark"):
        res = await srv._generate_chart(data=data, chart_type="bar", engine="plotly", theme=theme)
        assert res["success"] is True
        assert res["metadata"]["theme"] == theme 