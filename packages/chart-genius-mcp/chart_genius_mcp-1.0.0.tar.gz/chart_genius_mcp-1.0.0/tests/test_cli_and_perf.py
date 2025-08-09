import json
import os
import subprocess
import sys
import pytest

from chart_genius_mcp.core.performance import PerformanceMonitor


@pytest.mark.asyncio
async def test_performance_monitor_smoke():
    mon = PerformanceMonitor()
    await mon.start()
    await mon.record_chart_generation(12.3)
    stats = await mon.get_stats()
    assert stats["chart_generations"] >= 1
    assert "memory_usage_mb" in stats


def test_cli_version_and_validate_config():
    env = os.environ.copy()
    env["PYTHONPATH"] = "/Users/inwookbaek/Desktop/chart-genius-mcp/src"
    # Version
    out = subprocess.run(
        [sys.executable, "-m", "chart_genius_mcp", "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
    )
    assert out.returncode == 0
    assert "ChartGenius MCP Server v" in out.stdout or "ChartGenius MCP Server v" in out.stderr

    # Validate config (may print to stdout or stderr depending on environment)
    out2 = subprocess.run(
        [sys.executable, "-m", "chart_genius_mcp", "--validate-config"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
    )
    assert out2.returncode == 0
    assert ("Configuration" in out2.stderr) or ("Configuration" in out2.stdout) 