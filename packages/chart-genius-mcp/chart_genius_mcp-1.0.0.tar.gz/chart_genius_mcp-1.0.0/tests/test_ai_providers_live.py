import os
import pytest
import pandas as pd

from chart_genius_mcp.ai.providers import AiRouter

have_openai = bool(os.getenv("OPENAI_API_KEY"))
have_claude = bool(os.getenv("ANTHROPIC_API_KEY"))
have_gemini = bool(os.getenv("GOOGLE_API_KEY"))


@pytest.mark.asyncio
@pytest.mark.skipif(not have_openai, reason="OPENAI_API_KEY not set")
async def test_openai_live_smoke():
    router = AiRouter(enable_ai=True, preferred_order=["openai"], openai_api_key=os.getenv("OPENAI_API_KEY"))
    df = pd.DataFrame({"month": ["Jan", "Feb"], "sales": [100, 120]})
    res = await router.analyze_question("What is the trend?", df, "business")
    assert res["recommended_chart"] in {"bar", "line", "scatter", "pie", "heatmap", "histogram", "area", "box", "violin", "bubble"}


@pytest.mark.asyncio
@pytest.mark.skipif(not have_claude, reason="ANTHROPIC_API_KEY not set")
async def test_claude_live_smoke():
    router = AiRouter(enable_ai=True, preferred_order=["claude"], anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))
    df = pd.DataFrame({"c": ["A", "B"], "v": [1, 2]})
    res = await router.analyze_question("Compare categories", df, "business")
    assert res["recommended_chart"] in {"bar", "line", "scatter", "pie", "heatmap", "histogram", "area", "box", "violin", "bubble"}


@pytest.mark.asyncio
@pytest.mark.skipif(not have_gemini, reason="GOOGLE_API_KEY not set")
async def test_gemini_live_smoke():
    router = AiRouter(enable_ai=True, preferred_order=["gemini"], google_api_key=os.getenv("GOOGLE_API_KEY"))
    df = pd.DataFrame({"x": [0, 1], "y": [1, 3]})
    res = await router.analyze_question("Is there a relationship?", df, "technical")
    assert res["recommended_chart"] in {"bar", "line", "scatter", "pie", "heatmap", "histogram", "area", "box", "violin", "bubble"} 