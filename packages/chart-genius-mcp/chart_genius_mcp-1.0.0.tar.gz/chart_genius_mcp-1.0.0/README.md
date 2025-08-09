# 📊 ChartSmith MCP Server

**A high-performance chart generation MCP server** — built for speed, powered by AI, production-ready.

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io/)
[![Performance](https://img.shields.io/badge/Performance-39k+%20RPS-green)](./benchmarks/)
[![Charts](https://img.shields.io/badge/Chart%20Types-50+-orange)](./docs/chart-types.md)
[![Engines](https://img.shields.io/badge/Engines-4-purple)](./docs/engines.md)

> 🚀 **First-ever comprehensive chart generation MCP server** - Turn your SQL results into stunning visualizations with zero configuration and maximum performance.

## 🎯 **Why ChartGenius?**

### **💡 Inspired by Industry Leaders**
- **Hex.tech's $70M success** proves chart generation is core business infrastructure
- **Built to solve real bottlenecks** like O(n²) algorithms and blocking operations
- **MCP-native design** for seamless integration with any client

### **⚡ Performance First**
- Optimized O(n) data paths
- Concurrent rendering with guardrails (timeouts, semaphores, input caps)
- Intelligent caching (memory/Redis)

### **🧠 AI-Powered Intelligence**
- **Smart chart type detection** based on data patterns
- **Natural language to visualization** conversion
- **Automatic insight generation** for business intelligence
- **Accessibility optimization** for WCAG compliance

## 🚀 **Quick Start**

### **Installation**
```bash
pip install chart-genius-mcp  # package name remains; server id: chartsmith
```

### **Docker Quick Start**
```bash
docker build -t chartsmith-mcp .
docker run --rm -it chartsmith-mcp                 # stdio
docker run --rm -it -p 8000:8000 -e RUN_HTTP=1 chartsmith-mcp  # http
```

Using docker-compose:
```bash
docker compose up -d mcp-stdio
docker compose up -d mcp-http
```

## 🔌 Transports
- Stdio (MCP stdio)
- HTTP JSON (`POST /mcp`) and SSE (`POST /sse`)
- Health: `/health`, Readiness: `/ready`, Metrics: `/metrics`

## ⚙️ Environment
- `CHART_MAX_CONCURRENCY` (default 8)
- `CHART_TOOL_TIMEOUT_MS` (default 60000)
- `CHART_TOOL_TIMEOUT_MS_IMAGES` (image timeouts)
- `CHART_TOOL_TIMEOUT_MS_HEAVY` (batch/dashboard)
- `CHART_MAX_ROWS` (input size guard)
- `DISABLED_TOOLS` (comma-separated)
- AI: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `CHART_AI_PROVIDER`

## 🧰 Tools
- Per-chart: bar, line, scatter, histogram, area, box, violin, bubble, pie, heatmap, treemap, sunburst, sankey, choropleth
- Full-auto: `generate_chart_auto`
- Deprecated: `generate_chart`
- Cache: `manage_cache` (stats/clear/optimize)
- Perf: `get_performance_stats`
- Prompts/Resources: `list_prompts`/`get_prompt`, `list_resource_templates`/`read_resource`

## 📦 Resources
- Datasets: `dataset:sample/sales_small`, `.../scatter_small`, `.../heatmap_pivot`, `.../choropleth_iso3`
- Themes: `theme:modern`, `theme:corporate`, `theme:dark`, `theme:accessible`

## 🧪 Tests & Benchmarks
- Pytest suite: tools, engines, formats, AI (mock/live), cache, guardrails, MCP stdio/HTTP
- Benchmark harness: p50/p90 latency script and smoke tests

## 📈 Prometheus Metrics
- Endpoint: `/metrics` (Prometheus exposition format)
- Metrics include: request counts, tool call totals, tool errors, and duration histograms.
- Example scrape config:
```yaml
scrape_configs:
  - job_name: chartsmith
    static_configs:
      - targets: ['localhost:8000']
```

## 🔐 Security & Limits
- Input size caps, timeouts, concurrency limits
- Tool filtering via env

## 🧭 Smithery
- Stdio: configure Smithery to invoke `python -m chart_genius_mcp` with server id `chartsmith`
- HTTP: point Smithery at the container’s `/mcp` endpoint (port 8000)

## 📦 Docker Images (CI)
- GitHub Action builds and publishes multi-arch images to GHCR on tags `v*`.
- Image: `ghcr.io/<owner>/<repo>:<tag>` and `:latest`.
- Example pull:
```bash
docker pull ghcr.io/<owner>/<repo>:latest
``` 