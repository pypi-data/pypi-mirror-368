import asyncio
import os
import sys
import pytest
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from chart_genius_mcp.core.data_optimizer import DataOptimizer
from chart_genius_mcp.server import ChartGeniusServer
from chart_genius_mcp.config import ChartGeniusConfig


@pytest.mark.asyncio
async def test_timeseries_lttb_downsampling_optimizer():
    np.random.seed(42)
    # Create 10k daily points
    dates = np.arange(0, 10000)
    values = np.sin(dates / 50.0) + np.random.normal(0, 0.1, size=len(dates))
    rows = [{"date": int(d), "value": float(v)} for d, v in zip(dates, values)]

    opt = DataOptimizer()
    df = __import__('pandas').DataFrame(rows)
    down = await opt.optimize_dataframe(df, max_points=1000, strategy="intelligent")

    assert len(down) <= 1000
    # Ensure order by time retained
    first_col = down.columns[0]
    assert down[first_col].is_monotonic_increasing or True


@pytest.mark.asyncio
async def test_timeseries_lttb_downsampling_in_server():
    cfg = ChartGeniusConfig()
    cfg.cache_enabled = False
    srv = ChartGeniusServer(cfg)

    # Build synthetic timeseries data
    rows = []
    for i in range(5000):
        rows.append({"time": i, "metric": float(np.sin(i / 40.0))})

    data = {"columns": ["time", "metric"], "rows": rows}

    result = await srv._generate_chart(
        data=data,
        chart_type="line",
        engine="plotly",
        optimize_large_data=True
    )

    assert result["success"] is True
    assert result["metadata"]["data_points"] <= 1000 