import asyncio
import base64
import os
import sys
import pytest
import pytest_asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from chart_genius_mcp.server import ChartGeniusServer
from chart_genius_mcp.config import ChartGeniusConfig


@pytest_asyncio.fixture
async def server():
    cfg = ChartGeniusConfig()
    cfg.cache_enabled = False
    return ChartGeniusServer(cfg)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "engine,fmt,expects_base64",
    [
        ("plotly", "json", False),
        ("plotly", "html", False),
        ("plotly", "png", False),  # may fallback to json if kaleido not available
        ("matplotlib", "png", True),
        ("matplotlib", "svg", True),
        ("seaborn", "png", True),
        ("seaborn", "pdf", True),
    ],
)
async def test_export_formats(server, engine, fmt, expects_base64):
    data = {
        "columns": ["month", "sales"],
        "rows": [
            {"month": "Jan", "sales": 1000},
            {"month": "Feb", "sales": 1200},
            {"month": "Mar", "sales": 1100},
        ],
    }

    result = await server._generate_chart(
        data=data, chart_type="bar", engine=engine, format=fmt
    )

    assert result["success"] is True
    meta = result["metadata"]
    # Plotly may fallback to json when image export is not available
    if engine == "plotly" and fmt in {"png", "svg"} and meta.get("format") == "json":
        assert isinstance(result["chart"]["chart_data"], str)
        return

    assert meta.get("format") == fmt
    payload = result["chart"]["chart_data"]
    if expects_base64:
        assert isinstance(payload, str)
        # basic base64 sanity check
        try:
            base64.b64decode(payload, validate=True)
        except Exception:
            pytest.fail("Expected base64 payload for image export") 