# ChartSmith MCP — Smithery Integration

## Stdio
Add to your client config:

```json
{
  "mcpServers": {
    "chartsmith": {
      "command": "python",
      "args": ["-m", "chart_genius_mcp"],
      "env": {
        "CHART_MAX_CONCURRENCY": "8",
        "CHART_TOOL_TIMEOUT_MS": "60000"
      }
    }
  }
}
```

## HTTP (Streamable)
Run the server in HTTP mode:

```bash
python -m chart_genius_mcp --transport http --port 8000
```

Client calls:
```bash
curl -s -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "generate_bar_chart",
    "arguments": {
      "data": {"rows": [{"month": "Jan", "sales": 10}]},
      "x": "month", "y": "sales", "engine": "plotly", "format": "json"
    }
  }'
```

## Health & Metrics
- Health: `GET /health`
- Ready: `GET /ready`
- Metrics: `GET /metrics` (Prometheus) 