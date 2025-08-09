import os
import importlib
import pytest

from chart_genius_mcp.config import ChartGeniusConfig


def test_env_overrides_cache_and_engine(monkeypatch):
    monkeypatch.setenv("CHART_CACHE_ENABLED", "false")
    monkeypatch.setenv("CHART_DEFAULT_ENGINE", "matplotlib")
    cfg = ChartGeniusConfig()
    assert cfg.cache_enabled is False
    assert cfg.default_engine == "matplotlib"


def test_ai_toggle_disabled_without_key(monkeypatch, capsys):
    monkeypatch.setenv("CHART_AI_FEATURES", "true")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    cfg = ChartGeniusConfig()
    # Should auto-disable and warn
    assert cfg.enable_ai_features is False


def test_ai_toggle_enabled_with_key(monkeypatch):
    monkeypatch.setenv("CHART_AI_FEATURES", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    cfg = ChartGeniusConfig()
    assert cfg.enable_ai_features is True


def test_invalid_redis_requires_url(monkeypatch):
    monkeypatch.setenv("CHART_CACHE_TYPE", "redis")
    monkeypatch.delenv("REDIS_URL", raising=False)
    with pytest.raises(ValueError):
        ChartGeniusConfig() 