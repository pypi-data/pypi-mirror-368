import asyncio
import json as pyjson
import os
import pytest

import pandas as pd

from chart_genius_mcp.ai.providers import (
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    AiRouter,
)


@pytest.mark.asyncio
async def test_openai_provider_mapping(monkeypatch):
    async def fake_post(self, url, headers=None, json=None):
        class R:
            def raise_for_status(self):
                return None

            def json(self_inner):
                return {"output_text": response_text}

        # Return structured JSON string
        response_text = pyjson.dumps(
            {
                "recommended_chart": "line",
                "reasoning": "trend",
                "confidence": 0.82,
                "theme": "corporate",
            }
        )
        return R()

    import httpx

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post, raising=True)

    provider = OpenAIProvider(api_key="sk-test")
    df = pd.DataFrame({"month": ["Jan", "Feb"], "sales": [1, 2]})
    result = await provider.analyze_question("trend?", df, "business")
    assert result["recommended_chart"] == "line"
    assert 0.0 <= result["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_claude_provider_mapping(monkeypatch):
    async def fake_post(self, url, headers=None, json=None):
        class R:
            def raise_for_status(self):
                return None

            def json(self_inner):
                return {"content": [{"text": response_text}]}

        response_text = pyjson.dumps(
            {
                "recommended_chart": "bar",
                "reasoning": "compare",
                "confidence": 0.75,
                "theme": "modern",
            }
        )
        return R()

    import httpx

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post, raising=True)

    provider = AnthropicProvider(api_key="ak-test")
    df = pd.DataFrame({"c": ["A", "B"], "v": [1, 2]})
    result = await provider.analyze_question("compare?", df, "business")
    assert result["recommended_chart"] == "bar"


@pytest.mark.asyncio
async def test_gemini_provider_mapping(monkeypatch):
    async def fake_post(self, url, json=None):
        class R:
            def raise_for_status(self):
                return None

            def json(self_inner):
                return {"candidates": [{"content": {"parts": [{"text": response_text}]}}]}

        response_text = pyjson.dumps(
            {
                "recommended_chart": "scatter",
                "reasoning": "relationship",
                "confidence": 0.8,
                "theme": "modern",
            }
        )
        return R()

    import httpx

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post, raising=True)

    provider = GeminiProvider(api_key="gk-test")
    df = pd.DataFrame({"x": [0, 1], "y": [0.1, 0.2]})
    result = await provider.analyze_question("corr?", df, "technical")
    assert result["recommended_chart"] == "scatter"


@pytest.mark.asyncio
async def test_router_fallback_on_error(monkeypatch):
    async def raising_post(*args, **kwargs):
        class R:
            def raise_for_status(self):
                raise RuntimeError("boom")
        raise RuntimeError("boom")

    import httpx

    monkeypatch.setattr(httpx.AsyncClient, "post", raising_post, raising=True)

    router = AiRouter(
        enable_ai=True,
        preferred_order=["openai"],
        openai_api_key="sk-test",
    )
    df = pd.DataFrame({"x": [0, 1], "y": [1, 2]})
    res = await router.analyze_question("trend?", df, "business")
    assert res["recommended_chart"] in {"bar", "line", "scatter", "pie", "heatmap", "histogram", "area", "box", "violin", "bubble"} 