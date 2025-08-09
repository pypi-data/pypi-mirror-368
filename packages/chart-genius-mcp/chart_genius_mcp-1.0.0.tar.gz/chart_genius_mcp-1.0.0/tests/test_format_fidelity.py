import base64
import os
import sys
import pytest

from chart_genius_mcp.server import ChartGeniusServer
from chart_genius_mcp.config import ChartGeniusConfig


@pytest.mark.asyncio
async def test_svg_pdf_markers_matplotlib():
    cfg = ChartGeniusConfig()
    cfg.cache_enabled = False
    srv = ChartGeniusServer(cfg)
    data = {"columns": ["x", "y"], "rows": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]}

    # SVG
    res_svg = await srv._generate_chart(data=data, chart_type="line", engine="matplotlib", format="svg")
    svg_b64 = res_svg["chart"]["chart_data"]
    svg_bytes = base64.b64decode(svg_b64)
    assert b"<svg" in svg_bytes[:2000]

    # PDF
    res_pdf = await srv._generate_chart(data=data, chart_type="line", engine="seaborn", format="pdf")
    pdf_b64 = res_pdf["chart"]["chart_data"]
    pdf_bytes = base64.b64decode(pdf_b64)
    assert pdf_bytes.startswith(b"%PDF")


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get("SKIP_PLOTLY_KALEIDO", "0") == "1", reason="kaleido check skipped")
async def test_plotly_kaleido_png_svg_success_paths():
    cfg = ChartGeniusConfig()
    cfg.cache_enabled = False
    srv = ChartGeniusServer(cfg)
    data = {"columns": ["x", "y"], "rows": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]}

    # PNG
    r_png = await srv._generate_chart(data=data, chart_type="line", engine="plotly", format="png")
    fmt_png = r_png["metadata"]["format"]
    if fmt_png == "png":
        png_b64 = r_png["chart"]["chart_data"]
        _ = base64.b64decode(png_b64, validate=True)
    else:
        # fallback path still acceptable
        assert fmt_png in ("json", "html")

    # SVG
    r_svg = await srv._generate_chart(data=data, chart_type="line", engine="plotly", format="svg")
    fmt_svg = r_svg["metadata"]["format"]
    if fmt_svg == "svg":
        svg_b64 = r_svg["chart"]["chart_data"]
        svg_bytes = base64.b64decode(svg_b64)
        assert b"<svg" in svg_bytes[:2000]
    else:
        assert fmt_svg in ("json", "html") 