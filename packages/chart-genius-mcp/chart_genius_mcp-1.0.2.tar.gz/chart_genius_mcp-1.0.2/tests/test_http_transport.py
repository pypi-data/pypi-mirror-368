import json
import pytest
from chart_genius_mcp.server import ChartGeniusServer
from chart_genius_mcp.http_server import create_http_app
from fastapi.testclient import TestClient


def test_http_streamable_generate_chart():
    server = ChartGeniusServer()
    app = create_http_app(server, endpoint="/mcp")
    client = TestClient(app)

    payload = {
        "name": "generate_chart",
        "arguments": {
            "data": {
                "columns": ["x", "y"],
                "rows": [{"x": 0, "y": 1}, {"x": 1, "y": 3}],
            },
            "chart_type": "line",
            "engine": "plotly",
            "format": "json",
        },
    }

    r = client.post("/mcp", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body.get("success") is True
    assert body.get("format") in {"json", "html", "png", "svg", "pdf"} 