from __future__ import annotations

from typing import Any, Dict
import json
import asyncio

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, PlainTextResponse

from .server import ChartGeniusServer


def create_http_app(server: ChartGeniusServer, endpoint: str = "/mcp") -> FastAPI:
    app = FastAPI(title="ChartGenius MCP HTTP")

    # Streamable HTTP - list tools (lazy, no auth)
    @app.get(endpoint)
    async def list_tools_http():
        try:
            # Avoid heavy init during discovery
            try:
                server._ensure_initialized  # type: ignore[attr-defined]
            except Exception:
                pass
            tools = await server._list_tools_handler()  # type: ignore[attr-defined]
            tools_json = [t.model_dump() for t in tools]
            body = {"tools": tools_json}
            return JSONResponse(body)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # Streamable HTTP - call tool
    @app.post(endpoint)
    async def call_tool_http(payload: Dict[str, Any]):
        # Ensure heavy components are ready only when actually invoking tools
        try:
            server._ensure_initialized()  # type: ignore[attr-defined]
        except Exception:
            pass
        name = payload.get("name")
        arguments = payload.get("arguments") or {}
        if not name:
            return JSONResponse({"error": "Missing 'name' field"}, status_code=400)
        out = await server._call_tool_handler(name, arguments)  # type: ignore[attr-defined]
        # Tool handler returns [TextContent]; unwrap JSON string
        try:
            body = json.loads(out[0].text)
        except Exception:
            body = {"raw": out[0].text}
        return JSONResponse(body)

    # Streamable HTTP - end session (ack)
    @app.delete(endpoint)
    async def end_session_http():
        return JSONResponse({"ok": True})

    # Minimal SSE: one event with the full result
    @app.post("/sse")
    async def call_tool_sse(payload: Dict[str, Any]):
        try:
            server._ensure_initialized()  # type: ignore[attr-defined]
        except Exception:
            pass
        name = payload.get("name")
        arguments = payload.get("arguments") or {}
        if not name:
            return PlainTextResponse("", status_code=400)
        out = await server._call_tool_handler(name, arguments)  # type: ignore[attr-defined]
        try:
            body = json.loads(out[0].text)
        except Exception:
            body = {"raw": out[0].text}
        data = json.dumps(body)
        text = f"event: result\ndata: {data}\n\n"
        return Response(content=text, media_type="text/event-stream")

    # Health/Ready endpoints
    @app.get("/health")
    async def health():
        return JSONResponse({"status": "ok"})

    @app.get("/ready")
    async def ready():
        engines = getattr(server, "engines", {})
        return JSONResponse({"ready": bool(engines), "engines": list(engines.keys())})

    return app 